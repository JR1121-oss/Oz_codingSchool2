# app/apis/v1/patient_detail_apis.py
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.deps import get_current_user  
# deps.py의 실제 함수명으로 (STAFF/ADMIN 통과, PENDING 403)
# 토큰만 보고 통과시키므로 승인 대기 사용자도 환자 정보를 볼 수 있음
from app.models.patient import Patient
from app.schemas.patient import PatientUpdateRequest, PatientResponse

router = APIRouter()

async def _get_patient_or_404(db: AsyncSession, patient_id: int) -> Patient:
    patient = await db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="환자를 찾을 수 없습니다.")
    return patient


# REQ-PTNT-003: 환자 상세 조회
@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: int, db: AsyncSession = Depends(async_get_db)):
    return await _get_patient_or_404(db, patient_id)


# REQ-PTNT-004: 환자 정보 수정 (이름, 연락처)
@router.patch("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    update_data: PatientUpdateRequest,
    db: AsyncSession = Depends(async_get_db),
):
    patient = await _get_patient_or_404(db, patient_id)

    changes = update_data.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="수정할 항목을 하나 이상 입력해야 합니다.")

    for field, value in changes.items():
        setattr(patient, field, value)  # 스키마 필드명과 모델 속성명(phone vs phone_number)이 같아야 함
    patient.updated_at = datetime.now()

    await db.commit()
    await db.refresh(patient)
    return patient