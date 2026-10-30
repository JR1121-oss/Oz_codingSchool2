# app/ai/inference.py
"""C 파트: 흉부 X-ray 폐렴 예측 (EfficientNet-B0 + ResNet50 + ConvNeXt-Tiny 앙상블).

A&B 파트 서비스(prediction_service.py)와의 약속 (임시 파일을 교체하는 것이라 그대로 유지):
    predict(image_path: Path) -> PredictionOutput      # 동기 함수, 서비스가 asyncio.to_thread로 호출
D 파트 평가 스크립트(scripts/evaluate_model.py)가 가져다 쓰는 이름:
    load_models, THRESHOLD, IMG_SIZE, DEVICE           # 이름과 load_models()가 dict를 돌려주는 방식 유지

전처리/추론 방식은 학습 노트북(pneumonia_final.ipynb)과 동일하다.
    그레이스케일 -> autocontrast(cutoff=1) -> RGB -> 256x256 -> ImageNet 정규화
    -> softmax 폐렴(1) 확률 -> 좌우반전 TTA 평균 -> 3개 모델 평균 -> 임계값

==================== 팀과 얘기할 것 (코드 안에 태그) ====================
[논의 1]  confidence의 의미와 임계값 0.3의 어색함 (지금은 md/A&B 설계대로 "판정 확신도")
=================================================================================
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
# [논의 5] .pth 파일은 용량이 커서(특히 resnet50, convnext) git에 올리지 않는 걸 제안.
#          .gitignore에 app/ai/models/*.pth 추가 + 파일 공유 방법(드라이브 등)과 담당자 정하기.
#          GitHub는 100MB 초과 파일 푸시를 막는다. 크기는 du -h 로 확인.
MODEL_DIR = Path(__file__).resolve().parent / "models"

MODEL_FILES = {
    "efficientnet_b0": "efficientnet_b0.pth",
    "resnet50": "resnet50.pth",
    "convnext_tiny": "convnext_tiny.pth",
}

IMG_SIZE = 256

# [논의 2] 0.3은 노트북 결과 기준이다. md 4-1에 따르면 D 파트가 검증 데이터에서 Recall >= 0.90이
#          되도록 임계값을 정한다. D의 결과와 같은 값인지 확인 필요.
#          값이 바뀌면 MODEL_VERSION도 같이 올려야 결과 재사용(캐시)이 꼬이지 않는다.
THRESHOLD = 0.3

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# [논의 3] 서비스(prediction_service.py)는 settings.AI_MODEL_NAME을 쓰고, config.py에 없으면
#          기본값 "pneumonia-model-v1"을 쓴다. 이 상수는 서비스가 읽지 않아서 값이 어긋난다.
#          해결 방법 (A&B 담당자와 선택):
#            (a) config.py/.env에 AI_MODEL_NAME=pneumonia-ensemble-v1 을 넣는다.
#            (b) 서비스가 `from app.ai.inference import MODEL_VERSION`을 쓰게 바꾼다. (코드와 이름이 같이 바뀌어 안전)
#          가중치/임계값/전처리가 바뀌면 이름을 올려야 한다. 안 올리면 옛 결과가 계속 재사용된다. (50자 이내)
MODEL_VERSION = "pneumonia-ensemble-v1"

# 프로젝트 루트/media. 서비스의 MEDIA_DIR과 같은 위치다. (app/ai/inference.py 기준 parents[2])
MEDIA_DIR = (Path(__file__).resolve().parents[2] / "media").resolve()

# [논의 1] A&B 설계(md 결정 2)는 "예측한 판정에 대한 확신도"("predicted")라 그걸로 맞췄다.
#          그런데 임계값이 0.3이라 폐렴 확률 35%도 "폐렴"으로 판정되고, 그러면 "폐렴 35%"로 보인다.
#          "positive"(항상 폐렴 확률 저장)로 바꾸면 이 문제가 없다. 팀 합의 후 이 값만 바꾸면 된다.
#          어느 쪽이든 모델 3개 평균은 보정된 확률이 아니라 "점수"에 가깝다.
#          화면 문구도 "폐렴 확정"이 아니라 "의심" 같은 표현이 안전하다.
CONFIDENCE_MODE = "predicted"  # "predicted" | "positive"

# [논의 9] 히트맵은 선택사항이다. 시간이 부족하면 False로 끄면 heatmap_url은 항상 None이다.
#          DB의 heatmap_url이 nullable=False면 None 저장이 실패한다. 마이그레이션(md 결정 3) 확인 필요.
ENABLE_HEATMAP = True

# NFR-PRED-002: 추론 + 히트맵 목표 2초
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
    """이미지 파일을 읽을 수 없음.

    [논의 11] md는 이 경우 500 "X-ray 이미지 파일을 불러올 수 없습니다."로 정했는데, 서비스는
              predict의 모든 예외를 "AI 예측 중 오류가 발생했습니다."로 바꾼다.
              파일이 있는데 손상된 경우에만 해당하는 작은 차이다. 서비스에서 이 예외를 따로 잡으면 맞출 수 있다.
    """


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
        obj = torch.load(path, map_location="cpu", weights_only=True)
    except Exception:
        # [논의 10] 전체 모델(model.pth)은 pickle이라 weights_only로는 안 읽힌다.
        #           pickle은 파일 안의 코드가 실행될 수 있어서, 팀 내부에서 만든 파일일 때만 허용.
        #           가능하면 학습 쪽에서 state_dict로 다시 저장해서 이 fallback을 없애는 걸 제안.
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
    """모델을 한 번만 메모리에 올리고 이후에는 재사용한다. (스레드 안전, D 파트도 사용)

    [논의 7] 지금은 첫 호출 때 로딩한다. 서비스는 warmup()을 부르지 않아서 첫 요청이
             3초(NFR-PRED-002)를 넘길 수 있다. 서버 시작 시 warmup()을 부르는 게 좋다.
             main.py(팀장님 영역)에 lifespan 추가가 필요하니 상의 필요.
    """
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
    """서버 시작 시 한 번 호출하면 첫 요청이 느리지 않다. 모델 파일이 없으면 여기서 바로 실패한다."""
    load_models()


# ----------------------------------------------------------------------------
# 전처리 / 추론
# ----------------------------------------------------------------------------
def eval_transform(img: Image.Image) -> torch.Tensor:
    """(3, 256, 256) CPU 텐서. 서비스와 평가 스크립트가 같은 전처리를 쓰도록 공개한다.

    [논의 4] D 파트 evaluate_model.py는 Resize -> Grayscale만 하고 autocontrast가 없다.
             서비스(이 파일)와 학습 노트북은 autocontrast(cutoff=1)를 쓰므로, 평가한 Recall/Accuracy가
             실제 서비스 결과의 수치가 아니게 된다. D 파트가 아래처럼 이 함수를 쓰면 맞춰진다.
                 from app.ai.inference import eval_transform
                 dataset = datasets.ImageFolder(data_dir, transform=eval_transform)
    """
    img = img.convert("L")
    img = ImageOps.autocontrast(img, cutoff=1)
    img = img.convert("RGB")
    return _eval_tf(img)


def preprocess(img: Image.Image) -> torch.Tensor:
    """(1, 3, 256, 256) 텐서를 DEVICE에 올려 반환한다."""
    return eval_transform(img).unsqueeze(0).to(DEVICE)


@torch.inference_mode()
def _probabilities(x: torch.Tensor) -> dict:
    """전처리된 텐서로 폐렴 확률(0~1)을 구한다. 모델 3개 x 좌우반전 TTA.

    [논의 8] forward가 6회라 CPU에서는 느릴 수 있다. 실제 이미지로 시간을 재야 한다.
             (NFR-PRED-002 목표: 추론+히트맵 2초 이내)
             동시 요청이 여러 개 오면 CPU를 나눠 써서 더 느려지고 메모리도 늘어난다.
             서비스가 asyncio.to_thread로 부르므로 동시에 여러 번 실행될 수 있다.
             필요하면 동시 추론 수를 제한하는 방법을 검토.
    """
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

    heatmap_url = None
    if ENABLE_HEATMAP:
        try:
            relative = save_heatmap(load_models()["resnet50"], x, img, MEDIA_DIR)
            heatmap_url = f"/media/{relative}"
        except Exception:
            # 히트맵은 선택사항이라 실패해도 예측 결과는 돌려준다. (md: 생성하지 못하면 null)
            logger.exception("히트맵 생성 실패 (None으로 응답)")

    elapsed = time.perf_counter() - start
    if elapsed > SLOW_LOG_SECONDS:
        # [논의 8] 목표(2초)를 넘으면 로그를 남긴다. 성능 점검에 쓸 수 있다.
        logger.warning("예측이 %.2f초 걸렸습니다 (목표 %.1f초)", elapsed, SLOW_LOG_SECONDS)

    return PredictionOutput(
        is_pneumonia=is_pneumonia,
        confidence=_to_confidence(prob, is_pneumonia),
        heatmap_url=heatmap_url,
    )
