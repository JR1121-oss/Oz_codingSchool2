# scripts/evaluate_model.py
"""
NFR-PRED-001 모델 검증 스크립트
사용법:
    python -m scripts.evaluate_model --data_dir /path/to/test_dataset
"""
import argparse
from pathlib import Path
import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from tqdm import tqdm

from app.ai.inference import load_models, THRESHOLD, IMG_SIZE, DEVICE


def evaluate(data_dir: str):
    print(f"[*] 테스트 데이터셋 로드 중: {data_dir}")
    transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.Grayscale(num_output_channels=3),  # 3채널 통일
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    dataset = datasets.ImageFolder(data_dir, transform=transform)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=False, num_workers=4)

    # 클래스 인덱스 확인 (일반적으로 0: NORMAL, 1: PNEUMONIA)
    print(f"[*] 클래스 매핑: {dataset.class_to_idx}")
    
    models_dict = load_models()
    for m in models_dict.values():
        m.eval()

    tp, fp, fn, tn = 0, 0, 0, 0

    print("[*] 추론 및 평가 진행 중...")
    with torch.inference_mode():
        for inputs, labels in tqdm(dataloader):
            inputs = inputs.to(DEVICE)
            batch_size = inputs.size(0)

            # 앙상블 예측 확률 계산
            batch_probs = torch.zeros(batch_size, device=DEVICE)
            for name, model in models_dict.items():
                p = model(inputs).softmax(1)[:, 1]
                p_flip = model(torch.flip(inputs, dims=[3])).softmax(1)[:, 1]
                batch_probs += (p + p_flip) / 2
            
            batch_probs /= len(models_dict)
            preds = (batch_probs > THRESHOLD).long()
            
            # 정답 라벨 (PNEUMONIA가 1이라고 가정)
            true_labels = labels.to(DEVICE)

            tp += ((preds == 1) & (true_labels == 1)).sum().item()
            fp += ((preds == 1) & (true_labels == 0)).sum().item()
            fn += ((preds == 0) & (true_labels == 1)).sum().item()
            tn += ((preds == 0) & (true_labels == 0)).sum().item()

    total = tp + fp + fn + tn
    accuracy = (tp + tn) / total if total > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0

    print("\n" + "="*40)
    print(" 📊 모델 평가 결과 리포트 (NFR-PRED-001)")
    print("="*40)
    print(f" - 총 테스트 샘플 수 : {total}")
    print(f" - TP (환자를 환자로) : {tp}")
    print(f" - FN (환자를정상으로오진): {fn} (치명적 오류)")
    print(f" - FP (정상을 환자로오진): {fp}")
    print(f" - TN (정상을 정상으로) : {tn}")
    print("-" * 40)
    print(f" ✔ Recall (민감도)     : {recall:.4f} (기준: >= 0.90)")
    print(f" ✔ Accuracy (정확도)   : {accuracy:.4f} (기준: >= 0.80)")
    print(f" ✔ Precision (정밀도)  : {precision:.4f}")
    print("="*40)

    if recall >= 0.90 and accuracy >= 0.80:
        print("🎉 NFR-PRED-001 검증 기준을 충족했습니다! 배포 가능합니다.")
    else:
        print("⚠️ 기준 미달입니다. 임계값(THRESHOLD) 조정이나 추가 학습이 필요합니다.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, required=True, help="테스트 이미지 데이터셋 경로 (ImageFolder 형식)")
    args = parser.parse_args()
    evaluate(args.data_dir)