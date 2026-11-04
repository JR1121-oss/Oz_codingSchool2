# app/apis/v1/medical_record_detail_apis.py
# [Presentation] 진료기록 상세 / X-Ray 이미지 엔드포인트 (REQ-MDR-003)
# 요청을 받아 service를 호출하고 결과를 반환만 한다. 로직은 services/medical_record_service.py
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.deps import get_approved_user
from app.models.user import User
from app.schemas.medical_record import MedicalRecordDetailResponse
from app.services import medical_record_service as service

# prefix는 main.py에서 "/api/v1/medical-records"로 붙인다.
router = APIRouter()


# 최종 경로: GET /api/v1/medical-records/{record_id}
# 권한: get_approved_user가 PENDING(403)·비활성(401)을 막으므로 STAFF/ADMIN만 통과
@router.get("/{record_id}", response_model=MedicalRecordDetailResponse)
async def get_record(
    record_id: int,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_approved_user),
):
    return await service.get_medical_record(db, record_id)


# 최종 경로: GET /api/v1/medical-records/{record_id}/image
@router.get("/{record_id}/image")
async def get_record_image(
    record_id: int,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_approved_user),
):
    path = await service.get_record_image_path(db, record_id)
    return FileResponse(path)