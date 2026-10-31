# app/ai/heatmap.py
"""Grad-CAM 히트맵 생성. (선택 기능: 실패하면 호출하는 쪽(inference.py)에서 None으로 처리한다)

추가 라이브러리 없이 torch, numpy, PIL만 쓴다.
inference.py와 서로 import하면 순환이 생겨서, 모델과 입력 텐서는 인자로 받는다.
앙상블 3개 중 ResNet50 하나로만 히트맵을 만든다. (inference.py가 resnet50을 넘긴다)
"""
import uuid
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image

# 원본 X-ray는 수천 px일 수 있어서 긴 변을 줄여 저장한다. (속도와 파일 크기 때문)
MAX_SIDE = 512


def _colormap(cam: np.ndarray) -> np.ndarray:
    """0~1 값을 jet 계열 색으로 바꾼다. (H, W) -> (H, W, 3) uint8. matplotlib 없이 구현."""
    r = np.clip(1.5 - np.abs(4 * cam - 3), 0, 1)
    g = np.clip(1.5 - np.abs(4 * cam - 2), 0, 1)
    b = np.clip(1.5 - np.abs(4 * cam - 1), 0, 1)
    return (np.stack([r, g, b], axis=-1) * 255).astype(np.uint8)


def _grad_cam(model: nn.Module, x: torch.Tensor) -> np.ndarray:
    """폐렴(1) 클래스에 대한 Grad-CAM을 0~1 범위 (h, w) 배열로 반환한다.

    hook을 쓰지 않고 ResNet50 forward를 직접 풀어서 쓴다.
    (hook은 공유 모델에 동시 요청이 오면 서로 섞일 수 있어서 피했다)
    torchvision ResNet 구조가 아닌 모델이면 여기서 AttributeError가 난다.
    """
    x = x.detach().clone().requires_grad_(True)

    with torch.enable_grad():
        h = model.maxpool(model.relu(model.bn1(model.conv1(x))))
        feats = model.layer4(model.layer3(model.layer2(model.layer1(h))))
        logits = model.fc(torch.flatten(model.avgpool(feats), 1))
        grads = torch.autograd.grad(logits[0, 1], feats)[0]

    with torch.no_grad():
        weights = grads.mean(dim=(2, 3), keepdim=True)
        cam = F.relu((weights * feats).sum(dim=1))[0]  # (8, 8)

    cam = cam.detach().cpu().numpy()
    peak = cam.max()
    return cam / peak if peak > 0 else cam


def save_heatmap(model: nn.Module, x: torch.Tensor, img: Image.Image, media_dir: Path) -> str:
    """히트맵을 원본 위에 겹쳐 PNG로 저장하고, media 기준 상대경로를 반환한다.

    반환 예: "heatmaps/3f2a9c1e....png"  ->  inference.py가 "/media/" + 반환값으로 URL을 만든다.
    파일을 먼저 저장하고 DB 저장은 서비스가 나중에 하므로, DB 저장이 실패하면 파일만 남을 수 있다.
    """
    cam = _grad_cam(model, x)

    base = img.convert("L")
    w, h = base.size
    scale = MAX_SIDE / max(w, h)
    if scale < 1:
        base = base.resize((round(w * scale), round(h * scale)), Image.BILINEAR)

    cam_img = Image.fromarray((cam * 255).astype(np.uint8)).resize(base.size, Image.BICUBIC)
    heat = _colormap(np.asarray(cam_img, dtype=np.float32) / 255).astype(np.float32)
    gray = np.asarray(base.convert("RGB"), dtype=np.float32)
    overlay = np.clip(0.6 * gray + 0.4 * heat, 0, 255).astype(np.uint8)

    out_dir = media_dir / "heatmaps"
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.png"
    Image.fromarray(overlay).save(out_dir / filename)
    return f"heatmaps/{filename}"