# app/schemas/prediction.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PredictionResponse(BaseModel):
    """POST /{record_id}/predictions 응답 (REQ-PRED-001)"""

    model_config = ConfigDict(from_attributes=True)

    id: int                        # 예측 결과 고유 ID
    record_id: int                 # 진료기록 ID
    is_pneumonia: bool             # 폐렴 여부
    confidence: float              # 예측 확신도 (0~100, 소수 둘째 자리)
    heatmap_url: str | None        # 병변 표시 이미지 URL (선택사항)
    ai_model: str                  # 예측에 사용한 모델
    created_at: datetime           # 예측 수행 일시


class PredictionItem(BaseModel):
    """예측 결과 목록의 항목 1건 (REQ-PRED-002)"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_pneumonia: bool
    confidence: float
    heatmap_url: str | None
    created_at: datetime           # 예측 수행 일시
    ai_model: str                  # 사용한 모델


# [삭제] PredictionListResponse
#   목록 API가 프론트에 맞춰 객체({record_id, xray_image_url, items}) 대신
#   배열(list[PredictionItem])을 바로 돌려주게 바뀌어서 더 이상 쓰지 않는다.
