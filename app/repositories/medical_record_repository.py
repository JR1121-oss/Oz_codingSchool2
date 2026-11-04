# app/repositories/medical_record_repository.py
# [Data Access] 진료기록 / X-Ray 이미지 DB 쿼리만 담당한다. (REQ-MDR-001 ~ 003)
# - HTTP 예외(HTTPException)나 파일 처리는 하지 않는다 → services 계층의 역할
# - commit/rollback도 하지 않는다 → 트랜잭션 경계는 service가 정한다
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.JR_xray_image import XrayImage
from app.models.medical_record import MedicalRecord
from app.models.patient import Patient


async def get_patient_by_id(db: AsyncSession, patient_id: int) -> Patient | None:
    """환자 단건 조회 (존재 확인용)"""
    return await db.scalar(select(Patient).where(Patient.id == patient_id))


async def create_record(
    db: AsyncSession,
    *,
    patient_id: int,
    chart_number: str,
    symptoms: str,
) -> MedicalRecord:
    """진료기록 INSERT. flush로 record.id(PK)를 받아온다. (commit은 service에서)"""
    record = MedicalRecord(
        patient_id=patient_id,
        chart_number=chart_number,
        symptoms=symptoms,
    )
    db.add(record)
    await db.flush()
    return record


async def create_xray_image(
    db: AsyncSession,
    *,
    record_id: int,
    uploader_id: int | None,
    image_url: str,
    shooting_datetime: datetime,
) -> XrayImage:
    """X-Ray 이미지 INSERT (commit은 service에서)"""
    image = XrayImage(
        record_id=record_id,
        uploader_id=uploader_id,
        image_url=image_url,
        shooting_datetime=shooting_datetime,
    )
    db.add(image)
    return image


async def get_records_by_patient(db: AsyncSession, patient_id: int) -> list[MedicalRecord]:
    """특정 환자의 진료기록 목록 (최근 기록이 위로)"""
    result = await db.execute(
        select(MedicalRecord)
        .where(MedicalRecord.patient_id == patient_id)
        .order_by(MedicalRecord.id.desc())
    )
    return list(result.scalars().all())


async def get_record_by_id(db: AsyncSession, record_id: int) -> MedicalRecord | None:
    """진료기록 단건 조회"""
    return await db.scalar(select(MedicalRecord).where(MedicalRecord.id == record_id))


async def get_latest_image_url(db: AsyncSession, record_id: int) -> str | None:
    """진료기록의 가장 최근 X-Ray 이미지 경로
    (record.xray_images 로 읽으면 비동기 세션에서 lazy loading 에러가 나므로 따로 조회한다)
    """
    return await db.scalar(
        select(XrayImage.image_url)
        .where(XrayImage.record_id == record_id)
        .order_by(XrayImage.created_at.desc(), XrayImage.id.desc())
        .limit(1)
    )