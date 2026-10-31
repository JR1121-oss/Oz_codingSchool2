# app/services/patient_service.py
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enum import GenderEnum
from app.repositories import patient_repository as repo
from app.schemas.patient import PatientCreate, PatientUpdateRequest

PATIENT_NOT_FOUND = "환자를 찾을 수 없습니다."

# ---------- [추가] REQ-PTNT-001: 환자 등록 ----------
async def create_patient(db: AsyncSession, payload: PatientCreate):
    return await repo.create_patient(db, payload.model_dump())
 
 
# ---------- [추가] REQ-PTNT-002: 환자 목록 조회 ----------
async def get_patients(
    db: AsyncSession,
    name: str | None = None,
    gender: GenderEnum | None = None,
    min_age: int | None = None,
    max_age: int | None = None,
):
    # 최소 나이가 최대 나이보다 크면 결과가 항상 비므로 미리 알려준다
    if min_age is not None and max_age is not None and min_age > max_age:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="최소 나이는 최대 나이보다 클 수 없습니다.",
        )
    return await repo.get_patients(db, name, gender, min_age, max_age)


# ---------- REQ-PTNT-003: 환자 상세 조회 ----------
async def get_patient(db: AsyncSession, patient_id: int):
    """REQ-PTNT-003: 환자 상세 조회"""
    patient = await repo.get_patient_by_id(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=PATIENT_NOT_FOUND)
    return patient


# ---------- REQ-PTNT-004: 환자 정보 수정 ----------
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