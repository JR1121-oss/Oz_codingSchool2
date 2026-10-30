# app/services/patient_service.py
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import patient_repository as repo
from app.schemas.patient import PatientUpdateRequest

PATIENT_NOT_FOUND = "환자를 찾을 수 없습니다."


async def get_patient(db: AsyncSession, patient_id: int):
    """REQ-PTNT-003: 환자 상세 조회"""
    patient = await repo.get_patient_by_id(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=PATIENT_NOT_FOUND)
    return patient


async def update_patient(db: AsyncSession, patient_id: int, data: PatientUpdateRequest):
    """REQ-PTNT-004: 환자 정보 수정 (보낸 항목만)"""
    patient = await repo.get_patient_by_id(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=PATIENT_NOT_FOUND)

    # exclude_unset=True → 클라이언트가 실제로 보낸 필드만 추출
    fields = data.model_dump(exclude_unset=True, exclude_none=True)
    if not fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 항목을 하나 이상 입력해야 합니다.",
        )
    return await repo.update_patient(db, patient, fields)