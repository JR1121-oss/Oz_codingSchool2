# app/apis/v1/prediction_apis.py
# [Presentation] AI 폐렴 예측 엔드포인트 (REQ-PRED-001, 002)
# 경로와 응답 모양은 프론트(static/apis.js, pages.js)가 실제로 호출하는 형태에 맞췄다.
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.deps import get_approved_user
from app.models.user import User
from app.schemas.prediction import PredictionItem, PredictionResponse
from app.services import prediction_service

# prefix 는 main.py 에서 "/api/v1/medical-records" 로 붙인다
router = APIRouter()


# 파트 A: AI 폐렴 예측 (REQ-PRED-001)
# 최종 경로: POST /api/v1/medical-records/{record_id}/predict
@router.post(
    "/{record_id}/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="AI 폐렴 예측 (REQ-PRED-001)",
)
async def create_prediction(
    record_id: int,
    response: Response,
    db: AsyncSession = Depends(async_get_db),
    _: User = Depends(get_approved_user),  # STAFF, ADMIN 통과 / PENDING 403 / 비활성 401 (부서 무관)
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
# 최종 경로: GET /api/v1/medical-records/{record_id}/analyses
@router.get(
    "/{record_id}/analyses",
    response_model=list[PredictionItem],
    summary="AI 예측 결과 목록 조회 (REQ-PRED-002)",
)
async def list_predictions(
    record_id: int,
    db: AsyncSession = Depends(async_get_db),
    _: User = Depends(get_approved_user),
):
    """진료기록의 AI 예측 결과를 최신순 배열로 돌려준다. 결과가 없으면 빈 배열 []."""
    return await prediction_service.list_predictions(db, record_id)