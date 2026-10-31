# scripts/evaluate_model.py
"""
NFR-PRED-001 모델 검증 스크립트
사용법 (프로젝트 루트에서 실행):
    python -m scripts.evaluate_model --data_dir /path/to/test_dataset
"""
import argparse

import torch
from torch.utils.data import DataLoader
from torchvision import datasets
from tqdm import tqdm

# [변경] 전처리를 직접 만들지 않고 서비스(inference.py)와 같은 함수를 가져온다
from app.ai.inference import load_models, eval_transform, THRESHOLD, DEVICE


def evaluate(data_dir: str):
    print(f"[*] 테스트 데이터셋 로드 중: {data_dir}")

    # [변경] 서비스와 동일한 전처리
    #   그레이스케일 -> autocontrast(cutoff=1) -> RGB -> 256x256 -> ImageNet 정규화
    dataset = datasets.ImageFolder(data_dir, transform=eval_transform)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=False, num_workers=4)

    # [변경] PNEUMONIA 인덱스를 가정하지 않고 폴더 이름에서 찾는다
    print(f"[*] 클래스 매핑: {dataset.class_to_idx}")
    pneumonia_idx = next(
        (idx for name, idx in dataset.class_to_idx.items() if name.upper() == "PNEUMONIA"),
        None,
    )
    if pneumonia_idx is None:
        raise ValueError(f"PNEUMONIA 폴더를 찾을 수 없습니다: {dataset.class_to_idx}")

    models_dict = load_models()
    for m in models_dict.values():
        m.eval()

    # [변경] 서비스(_probabilities)와 같은 조건: GPU에서만 float16 autocast
    use_amp = DEVICE.type == "cuda"

    tp, fp, fn, tn = 0, 0, 0, 0

    print("[*] 추론 및 평가 진행 중...")
    with torch.inference_mode():
        for inputs, labels in tqdm(dataloader):
            inputs = inputs.to(DEVICE)
            batch_size = inputs.size(0)

            # 앙상블 예측 확률 계산 (모델 3개 x 좌우반전 TTA)
            batch_probs = torch.zeros(batch_size, device=DEVICE)
            for name, model in models_dict.items():
                with torch.autocast(device_type=DEVICE.type, dtype=torch.float16, enabled=use_amp):
                    p = model(inputs).float().softmax(1)[:, 1]
                    p_flip = model(torch.flip(inputs, dims=[3])).float().softmax(1)[:, 1]
                batch_probs += (p + p_flip) / 2

            batch_probs /= len(models_dict)
            preds = (batch_probs > THRESHOLD).long()

            # [변경] 폴더 매핑 기준으로 정답 라벨을 0/1로 변환
            true_labels = (labels == pneumonia_idx).long().to(DEVICE)

            tp += ((preds == 1) & (true_labels == 1)).sum().item()
            fp += ((preds == 1) & (true_labels == 0)).sum().item()
            fn += ((preds == 0) & (true_labels == 1)).sum().item()
            tn += ((preds == 0) & (true_labels == 0)).sum().item()

    total = tp + fp + fn + tn
    accuracy = (tp + tn) / total if total > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0

    print("\n" + "=" * 40)
    print(" 📊 모델 평가 결과 리포트 (NFR-PRED-001)")
    print("=" * 40)
    print(f" - 총 테스트 샘플 수 : {total}")
    print(f" - TP (환자를 환자로) : {tp}")
    print(f" - FN (환자를 정상으로 오진): {fn} (치명적 오류)")
    print(f" - FP (정상을 환자로 오진): {fp}")
    print(f" - TN (정상을 정상으로) : {tn}")
    print("-" * 40)
    print(f" ✔ Recall (민감도)     : {recall:.4f} (기준: >= 0.90)")
    print(f" ✔ Accuracy (정확도)   : {accuracy:.4f} (기준: >= 0.80)")
    print(f" ✔ Precision (정밀도)  : {precision:.4f}")
    print("=" * 40)

    if recall >= 0.90 and accuracy >= 0.80:
        print("🎉 NFR-PRED-001 검증 기준을 충족했습니다! 배포 가능합니다.")
    else:
        print("⚠️ 기준 미달입니다. 임계값(THRESHOLD) 조정이나 추가 학습이 필요합니다.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, required=True, help="테스트 이미지 데이터셋 경로 (ImageFolder 형식)")
    args = parser.parse_args()
    evaluate(args.data_dir)