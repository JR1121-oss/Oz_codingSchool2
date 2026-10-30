# app/repositories/patient_repository.py
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient


async def get_patient_by_id(db: AsyncSession, patient_id: int) -> Patient | None:
    """PK로 환자 1명 조회. 없으면 None"""
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    return result.scalar_one_or_none()


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