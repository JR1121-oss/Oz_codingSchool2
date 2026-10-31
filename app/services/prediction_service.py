# app/services/prediction_service.py
import asyncio
import logging
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.inference import predict
from app.core.config import settings
from app.models.JR_ai_analysis_results import AiAnalysisResult
from app.models.JR_xray_image import XrayImage
from app.models.medical_record import MedicalRecord
from app.schemas.prediction import PredictionItem, PredictionListResponse

logger = logging.getLogger(__name__)

# 사용할 모델 이름. config.py 에 AI_MODEL_NAME 이 없으면 기본값을 쓴다 (50자 이하).
AI_MODEL_NAME: str = getattr(settings, "AI_MODEL_NAME", "pneumonia-model-v1")

# 이 파일: <프로젝트 루트>/app/services/prediction_service.py
# parents[0]=services, [1]=app, [2]=프로젝트 루트
BASE_DIR = Path(__file__).resolve().parents[2]
MEDIA_DIR = (BASE_DIR / "media").resolve()


def _to_local_path(image_url: str) -> Path | None:
    """'/media/...' 로 저장된 URL 만 media 폴더 안의 로컬 파일로 바꾼다."""
    if not image_url or not image_url.startswith("/media/"):
        return None
    path = (BASE_DIR / image_url.lstrip("/")).resolve()
    return path if path.is_relative_to(MEDIA_DIR) else None


async def _ensure_record_exists(db: AsyncSession, record_id: int) -> None:
    exists = await db.scalar(select(MedicalRecord.id).where(MedicalRecord.id == record_id))
    if exists is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "진료기록을 찾을 수 없습니다.")


async def _latest_xray_url(db: AsyncSession, record_id: int) -> str | None:
    """한 진료기록에 이미지가 여러 장이면 가장 최근 1장."""
    return await db.scalar(
        select(XrayImage.image_url)
        .where(XrayImage.record_id == record_id)
        .order_by(XrayImage.created_at.desc(), XrayImage.id.desc())
        .limit(1)
    )


async def _find_saved_result(db: AsyncSession, record_id: int) -> AiAnalysisResult | None:
    """같은 진료기록, 같은 모델로 저장된 가장 최근 결과."""
    return await db.scalar(
        select(AiAnalysisResult)
        .where(
            AiAnalysisResult.record_id == record_id,
            AiAnalysisResult.ai_model == AI_MODEL_NAME,
        )
        .order_by(AiAnalysisResult.created_at.desc(), AiAnalysisResult.id.desc())
        .limit(1)
    )


async def get_or_create_prediction(
    db: AsyncSession, record_id: int
) -> tuple[AiAnalysisResult, bool]:
    """(예측 결과, 새로 만들었는지 여부)를 돌려준다. 저장된 결과가 있으면 추론하지 않는다."""
    # 1. 진료기록 확인
    await _ensure_record_exists(db, record_id)

    # 2. 같은 모델로 저장된 결과가 있으면 그대로 반환 (AI 추론 없음)
    saved = await _find_saved_result(db, record_id)
    if saved is not None:
        return saved, False

    # 3. 진료기록 저장 시 업로드한 X-ray 이미지 찾기
    image_url = await _latest_xray_url(db, record_id)
    if image_url is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "예측에 사용할 X-ray 이미지가 없습니다.")
    image_path = _to_local_path(image_url)
    if image_path is None or not image_path.is_file():
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "X-ray 이미지 파일을 불러올 수 없습니다."
        )

    # 4. AI 추론: CPU 연산이라 별도 스레드에서 실행해 서버가 멈추지 않게 한다
    try:
        output = await asyncio.to_thread(predict, image_path)
    except Exception:
        logger.exception("AI 예측 실패: record_id=%s", record_id)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "AI 예측 중 오류가 발생했습니다."
        )

    # 5. 결과 저장
    result = AiAnalysisResult(
        record_id=record_id,
        is_pneumonia=output.is_pneumonia,
        confidence=round(float(output.confidence), 2),
        heatmap_url=output.heatmap_url,
        ai_model=AI_MODEL_NAME,
    )
    db.add(result)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        # 동시에 같은 요청이 먼저 저장했다면(중복 방지 제약이 있을 때) 그 결과를 돌려준다
        saved = await _find_saved_result(db, record_id)
        if saved is not None:
            return saved, False
        logger.exception("예측 결과 저장 실패: record_id=%s", record_id)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "예측 결과를 저장하지 못했습니다."
        )
    await db.refresh(result)  # created_at 같은 DB 기본값을 읽어 온다
    return result, True


async def list_predictions(db: AsyncSession, record_id: int) -> PredictionListResponse:
    """진료기록의 예측 결과 전체를 최신순으로 돌려준다 (모델이 달라도 모두 포함)."""
    await _ensure_record_exists(db, record_id)
    xray_image_url = await _latest_xray_url(db, record_id)

    rows = await db.execute(
        select(AiAnalysisResult)
        .where(AiAnalysisResult.record_id == record_id)
        .order_by(AiAnalysisResult.created_at.desc(), AiAnalysisResult.id.desc())
    )
    items = [PredictionItem.model_validate(r) for r in rows.scalars().all()]
    return PredictionListResponse(
        record_id=record_id, xray_image_url=xray_image_url, items=items
    )
