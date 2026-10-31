# app/apis/v1/prediction_apis.py
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.deps import require_staff_or_admin
from app.models.user import User
from app.schemas.prediction import PredictionListResponse, PredictionResponse
from app.services import prediction_service

router = APIRouter()  # prefix 와 tags 는 main.py(또는 진료기록 라우터)가 붙여 준다


# 파트 A: AI 폐렴 예측 (REQ-PRED-001)
@router.post(
    "/{record_id}/predictions",
    response_model=PredictionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="AI 폐렴 예측 (REQ-PRED-001)",
)
async def create_prediction(
    record_id: int,
    response: Response,
    db: AsyncSession = Depends(async_get_db),
    _: User = Depends(require_staff_or_admin),  # STAFF, ADMIN 만 허용 (PENDING 은 403)
):
    """
    진료기록에 업로드된 X-ray 이미지로 폐렴을 예측한다.
    같은 모델로 저장된 결과가 있으면 추론 없이 그 결과를 200으로, 새로 예측하면 201로 응답한다.
    """
    result, created = await prediction_service.get_or_create_prediction(db, record_id)
    if not created:
        response.status_code = status.HTTP_200_OK
    return result


# 파트 B: AI 예측 결과 목록 조회 (REQ-PRED-002)
@router.get(
    "/{record_id}/predictions",
    response_model=PredictionListResponse,
    summary="AI 예측 결과 목록 조회 (REQ-PRED-002)",
)
async def list_predictions(
    record_id: int,
    db: AsyncSession = Depends(async_get_db),
    _: User = Depends(require_staff_or_admin),  # STAFF, ADMIN 만 허용 (PENDING 은 403)
):
    """진료기록의 X-ray 이미지와 AI 예측 결과를 최신순 목록으로 돌려준다. 결과가 없으면 items 는 빈 배열."""
    return await prediction_service.list_predictions(db, record_id)
