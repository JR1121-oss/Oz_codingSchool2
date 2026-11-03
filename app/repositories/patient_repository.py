# app/repositories/patient_repository.py
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enum import GenderEnum
from app.models.patient import Patient


# ---------- [추가] REQ-PTNT-001: 환자 등록 ----------
async def create_patient(db: AsyncSession, data: dict) -> Patient:
    """
    환자 1명 INSERT.
    스키마 필드명 = Patient 모델 속성명(name, age, gender, phone_number)이므로 그대로 넘긴다.
    """
    patient = Patient(**data)
    db.add(patient)
    await db.commit()
    await db.refresh(patient)  # id, created_at(DB 기본값) 읽어오기
    return patient
 
 
# ---------- [추가] REQ-PTNT-002: 환자 목록 조회 ----------
async def get_patients(
    db: AsyncSession,
    name: str | None = None,
    gender: GenderEnum | None = None,
    min_age: int | None = None,
    max_age: int | None = None,
) -> list[Patient]:
    """조건이 들어온 것만 WHERE에 붙여서 조회 (최근 등록 순)"""
    stmt = select(Patient)
    if name:
        stmt = stmt.where(Patient.name.like(f"%{name}%"))  # 이름 부분 일치
    if gender is not None:
        stmt = stmt.where(Patient.gender == gender)
    if min_age is not None:
        stmt = stmt.where(Patient.age >= min_age)
    if max_age is not None:
        stmt = stmt.where(Patient.age <= max_age)
    stmt = stmt.order_by(Patient.id.desc())
 
    result = await db.execute(stmt)
    return list(result.scalars().all())


# ---------- REQ-PTNT-003: 환자 상세 조회 ----------
async def get_patient_by_id(db: AsyncSession, patient_id: int) -> Patient | None:
    """PK로 환자 1명 조회. 없으면 None"""
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    return result.scalar_one_or_none()


# ---------- REQ-PTNT-004: 환자 정보 수정 ----------
async def update_patient(db: AsyncSession, patient: Patient, fields: dict) -> Patient:
    """
    전달된 필드만 수정합니다.
    스키마 필드명 = Patient 모델 속성명(name, phone_number)이므로 그대로 setattr
    """
    for key, value in fields.items():
        setattr(patient, key, value)
    patient.updated_at = datetime.now()

    await db.commit()
    await db.refresh(patient)
    return patient