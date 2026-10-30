# app/apis/v1/patient_detail_apis.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.deps import get_approved_user, get_medical_user
from app.models.user import User
from app.schemas.patient import PatientResponse, PatientUpdateRequest
from app.services import patient_service as service

# prefix는 main.py에서 "/api/v1/patients"로 지정하므로 여기서는 비워둔다.
router = APIRouter()


# REQ-PTNT-003: 환자 상세 정보 조회 API / 권한: 승인된 사용자 (PENDING은 403)
@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_approved_user),
):
    """환자 PK(patient_id)로 상세 정보를 조회합니다."""
    return await service.get_patient(db, patient_id)


# REQ-PTNT-004: 환자 정보 수정 API / 권한: 의료진 부서 + 승인된 사용자
@router.patch("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    update_data: PatientUpdateRequest,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_medical_user),
):
    """환자의 이름·연락처를 선택적으로 수정합니다. (보낸 항목만)"""
    return await service.update_patient(db, patient_id, update_data)