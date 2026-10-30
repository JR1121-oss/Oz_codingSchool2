# app/ai/inference.py
"""C 파트: 흉부 X-ray 폐렴 예측 (EfficientNet-B0 + ResNet50 + ConvNeXt-Tiny 앙상블).

서비스(prediction_service.py)가 쓰는 것:
    predict(image_path: Path) -> PredictionOutput   # 동기 함수, asyncio.to_thread로 호출
평가 스크립트(scripts/evaluate_model.py)가 쓰는 것:
    load_models, eval_transform, THRESHOLD, DEVICE

전처리/추론은 학습 노트북(pneumonia_final.ipynb)과 같다.
    그레이스케일 -> autocontrast(cutoff=1) -> RGB -> 256x256 -> ImageNet 정규화
    -> softmax 폐렴(1) 확률 -> 좌우반전 TTA 평균 -> 3개 모델 평균 -> 임계값
"""
import logging
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import torch
import torch.nn as nn
from PIL import Image, ImageOps
from torchvision import models, transforms

from app.ai.heatmap import save_heatmap

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------
# 설정
# ----------------------------------------------------------------------------
# .pth 파일은 용량 문제로 git에 올리지 않는다. (.gitignore: app/ai/models/*.pth)
MODEL_DIR = Path(__file__).resolve().parent / "models"

MODEL_FILES = {
    "efficientnet_b0": "efficientnet_b0.pth",
    "resnet50": "resnet50.pth",
    "convnext_tiny": "convnext_tiny.pth",
}

IMG_SIZE = 256

# [논의 2] 0.3은 노트북 결과 기준이다. 검증 데이터에서 Recall >= 0.90이 되는 값과 같은지
#          evaluate_model.py로 확인해야 한다. 값이 바뀌면 MODEL_VERSION도 같이 올린다.
THRESHOLD = 0.3

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# [논의 3] 서비스는 settings.AI_MODEL_NAME(기본값 "pneumonia-model-v1")을 쓰고 이 상수는 읽지 않는다.
#          (a) .env/config.py에 AI_MODEL_NAME=pneumonia-ensemble-v1 설정, 또는
#          (b) 서비스가 `from app.ai.inference import MODEL_VERSION`을 쓰게 변경 중 선택.
#          가중치/임계값/전처리가 바뀌면 이름을 올려야 저장된 옛 결과가 재사용되지 않는다. (50자 이내)
MODEL_VERSION = "pneumonia-ensemble-v1"

# 프로젝트 루트/media. 서비스의 MEDIA_DIR과 같은 위치다.
MEDIA_DIR = (Path(__file__).resolve().parents[2] / "media").resolve()

# [논의 1] "predicted": 판정한 쪽의 확신도 (API 설계 결정 2). 임계값이 0.3이라 폐렴 확률 35%도
#          "폐렴 35%"로 보이는 어색함이 있다. "positive"(항상 폐렴 확률)로 바꾸면 해결되며 이 값만 바꾸면 된다.
CONFIDENCE_MODE = "predicted"  # "predicted" | "positive"

# 히트맵은 선택 기능이다. False로 끄면 heatmap_url은 항상 None이다.
ENABLE_HEATMAP = True

# NFR-PRED-002: 추론 + 히트맵 목표 2초. 넘으면 경고 로그를 남긴다.
SLOW_LOG_SECONDS = 2.0

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
# 반환 형태 / 예외
# ----------------------------------------------------------------------------
@dataclass
class PredictionOutput:
    is_pneumonia: bool
    confidence: float  # 0~100 (%), 소수 둘째 자리
    heatmap_url: Optional[str]  # '/media/heatmaps/xxx.png' 형태. 만들지 못했으면 None


class PredictionError(Exception):
    """모델 로딩/추론 실패."""


class ImageLoadError(PredictionError):
    """이미지 파일을 읽을 수 없음 (손상된 파일 등)."""


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
    """state_dict 파일을 우선 읽고, 안 되면 전체 모델 파일(pickle)을 읽는다."""
    try:
        obj = torch.load(path, map_location="cpu", weights_only=True)
    except Exception:
        # 전체 모델 파일은 pickle이라 파일 안의 코드가 실행될 수 있다. 팀에서 만든 파일일 때만 사용한다.
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
        obj = {k.removeprefix("module."): v for k, v in obj.items()}  # DataParallel 접두사 제거
        model.load_state_dict(obj)

    return model.to(DEVICE).eval()


def load_models() -> dict:
    """모델을 한 번만 메모리에 올리고 이후에는 재사용한다. (스레드 안전, 평가 스크립트도 사용)"""
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


def warmup() -> None:
    """[논의 4] 서버 시작 시 한 번 호출하면 첫 요청이 느리지 않다. 모델 파일이 없으면 여기서 바로 실패한다.
    서비스는 아직 부르지 않는다. main.py에 lifespan으로 추가해야 한다.
    """
    load_models()


# ----------------------------------------------------------------------------
# 전처리 / 추론
# ----------------------------------------------------------------------------
def eval_transform(img: Image.Image) -> torch.Tensor:
    """(3, 256, 256) CPU 텐서. 서비스와 평가 스크립트가 같은 전처리를 쓰도록 공개한다."""
    img = img.convert("L")
    img = ImageOps.autocontrast(img, cutoff=1)
    img = img.convert("RGB")
    return _eval_tf(img)


def preprocess(img: Image.Image) -> torch.Tensor:
    """(1, 3, 256, 256) 텐서를 DEVICE에 올려 반환한다."""
    return eval_transform(img).unsqueeze(0).to(DEVICE)


@torch.inference_mode()
def _probabilities(x: torch.Tensor) -> dict:
    """전처리된 텐서로 폐렴 확률(0~1)을 구한다. 모델 3개 x 좌우반전 TTA."""
    use_amp = DEVICE.type == "cuda"
    per_model = {}
    for name, model in load_models().items():
        with torch.autocast(device_type=DEVICE.type, dtype=torch.float16, enabled=use_amp):
            p = model(x).float().softmax(1)[:, 1]
            p_flip = model(torch.flip(x, dims=[3])).float().softmax(1)[:, 1]
        per_model[name] = float((p + p_flip).item() / 2)  # 좌우반전 TTA

    prob = sum(per_model.values()) / len(per_model)  # 3개 모델 평균
    return {"probability": prob, "model_probabilities": per_model}


def _to_confidence(prob: float, is_pneumonia: bool) -> float:
    if CONFIDENCE_MODE == "positive":
        value = prob
    else:  # "predicted": 판정한 쪽의 확신도
        value = prob if is_pneumonia else 1 - prob
    return round(value * 100, 2)


def predict(image_path: Path) -> PredictionOutput:
    """X-ray 이미지 파일 1장을 예측한다. 동기 함수다.

    서비스가 `await asyncio.to_thread(predict, image_path)`로 부른다.
    image_path의 안전성(media 폴더 밖으로 나가지 않는지, 파일이 있는지)은 서비스에서 이미 확인한다.
    """
    start = time.perf_counter()

    try:
        img = Image.open(image_path)
        img.load()  # 여기서 깨진 파일을 바로 잡는다
    except (OSError, ValueError, Image.DecompressionBombError) as e:
        raise ImageLoadError(f"이미지를 읽을 수 없습니다: {image_path}") from e

    try:
        # 전처리는 inference_mode 밖에서 한다. 안에서 만든 텐서는 히트맵(역전파)에 쓸 수 없다.
        x = preprocess(img)
        out = _probabilities(x)
    except Exception as e:  # 모델 파일 없음, 형식 불일치, 메모리 부족 등
        raise PredictionError("모델 추론에 실패했습니다.") from e

    prob = out["probability"]
    is_pneumonia = prob > THRESHOLD

    # [논의 5] 히트맵은 ResNet50 한 모델 기준이라 "최종 판정 전체"가 아니라 "ResNet50이 본 영역"이다.
    #          화면 문구를 이에 맞춰야 하고, 만들지 못하면 None이므로 DB heatmap_url은 nullable이어야 한다.
    heatmap_url = None
    if ENABLE_HEATMAP:
        try:
            relative = save_heatmap(load_models()["resnet50"], x, img, MEDIA_DIR)
            heatmap_url = f"/media/{relative}"
        except Exception:
            # 히트맵은 선택 기능이라 실패해도 예측 결과는 돌려준다.
            logger.exception("히트맵 생성 실패 (None으로 응답)")

    elapsed = time.perf_counter() - start
    if elapsed > SLOW_LOG_SECONDS:
        logger.warning("예측이 %.2f초 걸렸습니다 (목표 %.1f초)", elapsed, SLOW_LOG_SECONDS)

    return PredictionOutput(
        is_pneumonia=is_pneumonia,
        confidence=_to_confidence(prob, is_pneumonia),
        heatmap_url=heatmap_url,
    )