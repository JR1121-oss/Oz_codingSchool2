# worker/model.py
"""흉부 X-ray 폐렴 예측 모델 (EfficientNet-B0 + ResNet50 + ConvNeXt-Tiny 앙상블).

- 모델 파일은 worker/models/ 에 두고, 처음 한 번만 메모리에 올린다.
- 전처리/추론 방식은 학습 노트북(pneumonia_final.ipynb)과 동일하게 맞췄다.
    그레이스케일 -> autocontrast(cutoff=1) -> RGB -> 256x256 리사이즈 -> ImageNet 정규화
    -> softmax 폐렴(1) 확률 -> 좌우반전 TTA 평균 -> 3개 모델 평균 -> 임계값 0.3
"""
import io
import threading
from pathlib import Path
from typing import Union

import torch
import torch.nn as nn
from PIL import Image, ImageOps
from torchvision import models, transforms

# ----------------------------------------------------------------------------
# 설정 (모델 파일 이름이 다르면 MODEL_FILES 만 수정하면 된다)
# ----------------------------------------------------------------------------
MODEL_DIR = Path(__file__).resolve().parent / "models"

MODEL_FILES = {
    "efficientnet_b0": "efficientnet_b0.pth",
    "resnet50": "resnet50.pth",
    "convnext_tiny": "convnext_tiny.pth",
}

IMG_SIZE = 256
THRESHOLD = 0.3  # 노트북에서 가장 성능이 좋았던 값 (0.5 보다 폐렴을 덜 놓친다)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_eval_tf = transforms.Compose(
    [
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ]
)

_models: dict = {}
_lock = threading.Lock()


# ----------------------------------------------------------------------------
# 모델 로드
# ----------------------------------------------------------------------------
def _build(name: str) -> nn.Module:
    """학습 때와 같은 구조(출력 2개)를 만든다. 사전학습 가중치는 받지 않는다."""
    if name == "efficientnet_b0":
        m = models.efficientnet_b0(weights=None)
        m.classifier[1] = nn.Linear(m.classifier[1].in_features, 2)
    elif name == "resnet50":
        m = models.resnet50(weights=None)
        m.fc = nn.Linear(m.fc.in_features, 2)
    elif name == "convnext_tiny":
        m = models.convnext_tiny(weights=None)
        m.classifier[2] = nn.Linear(m.classifier[2].in_features, 2)
    else:
        raise ValueError(f"지원하지 않는 모델: {name}")
    return m


def _load_one(name: str, path: Path) -> nn.Module:
    """state_dict 파일과 전체 모델 파일을 모두 처리한다."""
    try:
        # 가중치만 들어 있는 파일이면 안전 모드(weights_only)로 읽힌다.
        obj = torch.load(path, map_location="cpu", weights_only=True)
    except Exception:
        # 전체 모델(model.pth)은 pickle 이라 weights_only 로는 안 읽힌다.
        # 팀 내부에서 만든 파일일 때만 사용할 것 (출처 불명 파일 금지).
        obj = torch.load(path, map_location="cpu", weights_only=False)

    if isinstance(obj, nn.Module):
        model = obj
    else:
        if isinstance(obj, dict):
            for key in ("model_state_dict", "state_dict"):
                if key in obj:
                    obj = obj[key]
                    break
        model = _build(name)
        # DataParallel 로 저장된 경우의 "module." 접두사 제거
        obj = {k.removeprefix("module."): v for k, v in obj.items()}
        model.load_state_dict(obj)

    return model.to(DEVICE).eval()


def load_models() -> dict:
    """모델을 한 번만 메모리에 올리고 이후에는 재사용한다. (스레드 안전)"""
    global _models
    if _models:
        return _models
    with _lock:
        if _models:
            return _models
        loaded = {}
        for name, filename in MODEL_FILES.items():
            path = MODEL_DIR / filename
            if not path.exists():
                raise FileNotFoundError(f"모델 파일이 없습니다: {path}")
            loaded[name] = _load_one(name, path)
        _models = loaded
    return _models


# ----------------------------------------------------------------------------
# 추론
# ----------------------------------------------------------------------------
def _preprocess(image: Union[bytes, str, Path, Image.Image]) -> torch.Tensor:
    if isinstance(image, (bytes, bytearray)):
        img = Image.open(io.BytesIO(image))
    elif isinstance(image, Image.Image):
        img = image
    else:
        img = Image.open(image)
    img = img.convert("L")
    img = ImageOps.autocontrast(img, cutoff=1)
    img = img.convert("RGB")
    return _eval_tf(img).unsqueeze(0).to(DEVICE)  # (1, 3, 256, 256)


@torch.inference_mode()
def predict(image: Union[bytes, str, Path, Image.Image]) -> dict:
    """업로드된 X-ray 이미지 1장으로 폐렴 여부를 예측한다.

    image: 업로드 파일의 bytes, 파일 경로, 또는 PIL.Image
    반환 예:
        {"label": "PNEUMONIA", "is_pneumonia": True, "probability": 0.8731,
         "threshold": 0.3, "model_probabilities": {"efficientnet_b0": 0.91, ...}}
    """
    x = _preprocess(image)
    use_amp = DEVICE.type == "cuda"

    per_model = {}
    for name, model in load_models().items():
        with torch.autocast(device_type=DEVICE.type, dtype=torch.float16, enabled=use_amp):
            p = model(x).float().softmax(1)[:, 1]
            p_flip = model(torch.flip(x, dims=[3])).float().softmax(1)[:, 1]
        per_model[name] = float((p + p_flip).item() / 2)  # 좌우반전 TTA

    prob = sum(per_model.values()) / len(per_model)  # 3개 모델 평균
    is_pneumonia = prob > THRESHOLD
    return {
        "label": "PNEUMONIA" if is_pneumonia else "NORMAL",
        "is_pneumonia": is_pneumonia,
        "probability": round(prob, 4),
        "threshold": THRESHOLD,
        "model_probabilities": {k: round(v, 4) for k, v in per_model.items()},
    }


if __name__ == "__main__":
    # 로컬 확인용: python -m worker.model 샘플이미지.jpeg
    import json
    import sys

    print(json.dumps(predict(sys.argv[1]), ensure_ascii=False, indent=2))