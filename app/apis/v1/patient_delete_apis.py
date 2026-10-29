# app/apis/v1/patient_delete_apis.py
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.deps import get_current_user
from app.models.enum import RoleEnum
from app.models.JR_xray_image import XrayImage
from app.models.medical_record import MedicalRecord  
from app.models.JR_ai_analysis_results import AiAnalysisResult
from app.models.patient import Patient    
from app.models.user import User

router = APIRouter()  # prefix 와 tags 는 main.py 가 붙여 준다

# 이 파일: <프로젝트 루트>/app/apis/v1/patient_delete_apis.py
# parents[0]=v1, [1]=apis, [2]=app, [3]=프로젝트 루트 (폴더 위치를 바꾸면 이 숫자도 바꿔야 한다)
BASE_DIR = Path(__file__).resolve().parents[3]
MEDIA_DIR = (BASE_DIR / "media").resolve()


def _to_local_path(image_url: str) -> Path | None:
    """'/media/...' 로 저장된 URL 만 media 폴더 안의 로컬 파일로 바꾼다. 그 외는 건너뜀."""
    if not image_url or not image_url.startswith("/media/"):
        return None
    path = (BASE_DIR / image_url.lstrip("/")).resolve()
    return path if path.is_relative_to(MEDIA_DIR) else None  # media 폴더 밖은 삭제하지 않음


@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: int,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user),  # 로그인한 사용자만 삭제 가능
):
    # 1. 권한 확인: STAFF, ADMIN 만 허용하기
    if current_user.role not in (RoleEnum.STAFF, RoleEnum.ADMIN):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "접근 권한이 없습니다.")

    # 2. 환자 존재 확인
    exists = await db.scalar(select(Patient.id).where(Patient.id == patient_id))
    if exists is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "환자를 찾을 수 없습니다.")

    # 3. DB 행을 지우기 전에, 삭제할 파일(X-ray 이미지, AI 히트맵)의 URL 을 먼저 모아둔다
    xray_result = await db.execute(
        select(XrayImage.image_url)
        .join(MedicalRecord, XrayImage.record_id == MedicalRecord.id)
        .where(MedicalRecord.patient_id == patient_id)
    )
    heatmap_result = await db.execute(
        select(AiAnalysisResult.heatmap_url)
        .join(MedicalRecord, AiAnalysisResult.record_id == MedicalRecord.id)
        .where(MedicalRecord.patient_id == patient_id)
    )
    file_urls = [*xray_result.scalars().all(), *heatmap_result.scalars().all()]

    # 4. DB 삭제 
    await db.execute(delete(MedicalRecord).where(MedicalRecord.patient_id == patient_id))
    await db.execute(delete(Patient).where(Patient.id == patient_id))
    await db.commit()  # xray_images, ai_analysis_results 행은 record_id 의 ON DELETE CASCADE 로 함께 삭제

    # 5. DB 삭제가 성공한 뒤에 파일 삭제 
    for url in file_urls:
        path = _to_local_path(url)
        if path is not None:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass

    return {"message": "환자 및 관련 데이터가 삭제되었습니다."}