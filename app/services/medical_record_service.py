# app/services/medical_record_service.py
# [Business Logic] 진료기록 비즈니스 로직 (REQ-MDR-001 ~ 003)
# - 존재 여부 확인 및 예외 처리, X-Ray 파일 저장/삭제, 트랜잭션(commit/rollback), 응답 변환
# - DB 쿼리는 repositories/medical_record_repository.py 에 맡긴다
import asyncio
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import medical_record_repository as repo
from app.schemas.medical_record import MedicalRecordDetailResponse

# 이 파일: <루트>/app/services/medical_record_service.py -> parents[2]가 프로젝트 루트
BASE_DIR = Path(__file__).resolve().parents[2]
MEDIA_DIR = (BASE_DIR / "media").resolve()
MEDIA_URL_PREFIX = "/media"  # main.py의 StaticFiles 마운트, 환자 삭제 코드와 같은 형식

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}


# ---------- 내부 헬퍼 ----------
def _save_upload(file_obj, path: Path) -> None:
    """파일 저장(동기 I/O). 이벤트 루프를 막지 않도록 스레드에서 실행한다."""
    with open(path, "wb") as f:
        shutil.copyfileobj(file_obj, f)


def _to_detail(record, image_url: str | None) -> MedicalRecordDetailResponse:
    return MedicalRecordDetailResponse(
        id=record.id,
        patient_id=record.patient_id,
        chart_number=record.chart_number,
        symptoms=record.symptoms,
        xray_image_url=image_url,
        created_at=record.created_at,
    )


async def _ensure_patient_exists(db: AsyncSession, patient_id: int) -> None:
    if await repo.get_patient_by_id(db, patient_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "환자를 찾을 수 없습니다.")


# ---------- REQ-MDR-001: 진료기록 등록 ----------
async def create_medical_record(
    db: AsyncSession,
    *,
    patient_id: int,
    chart_number: str,
    symptoms: str,
    xray_image: UploadFile,
    uploader_id: int,
) -> MedicalRecordDetailResponse:
    # 1. 환자 존재 확인
    await _ensure_patient_exists(db, patient_id)

    # 2. 이미지 확장자 확인
    ext = os.path.splitext(xray_image.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "png, jpg, jpeg 이미지만 업로드할 수 있습니다."
        )

    # 3. 파일 저장: uuid 파일명으로 경로 조작과 이름 충돌을 막는다
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = MEDIA_DIR / filename
    await asyncio.to_thread(_save_upload, xray_image.file, file_path)
    image_url = f"{MEDIA_URL_PREFIX}/{filename}"

    # 4. DB 저장: 진료기록 + X-Ray 이미지를 한 트랜잭션으로
    try:
        record = await repo.create_record(
            db, patient_id=patient_id, chart_number=chart_number, symptoms=symptoms
        )
        await repo.create_xray_image(
            db,
            record_id=record.id,
            uploader_id=uploader_id,
            image_url=image_url,
            shooting_datetime=datetime.now(),  # 프론트가 촬영일시를 보내지 않으므로 등록 시각 사용
        )
        await db.commit()
    except Exception:
        await db.rollback()
        file_path.unlink(missing_ok=True)  # DB 저장에 실패하면 파일도 지운다
        raise

    await db.refresh(record)
    return _to_detail(record, image_url)


# ---------- REQ-MDR-002: 환자별 진료기록 목록 ----------
async def get_patient_records(db: AsyncSession, patient_id: int):
    await _ensure_patient_exists(db, patient_id)
    # 증상 100자 축약은 MedicalRecordListItem 스키마의 validator가 처리
    return await repo.get_records_by_patient(db, patient_id)


# ---------- REQ-MDR-003: 진료기록 상세 ----------
async def get_medical_record(db: AsyncSession, record_id: int) -> MedicalRecordDetailResponse:
    record = await repo.get_record_by_id(db, record_id)
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "진료 기록을 찾을 수 없습니다.")

    image_url = await repo.get_latest_image_url(db, record_id)
    return _to_detail(record, image_url)


async def get_record_image_path(db: AsyncSession, record_id: int) -> Path:
    """진료기록의 X-Ray 이미지 실제 파일 경로 (media 폴더 밖 파일은 거부)"""
    image_url = await repo.get_latest_image_url(db, record_id)
    if image_url is None or not image_url.startswith(f"{MEDIA_URL_PREFIX}/"):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "이미지를 찾을 수 없습니다.")

    path = (BASE_DIR / image_url.lstrip("/")).resolve()
    if not path.is_relative_to(MEDIA_DIR) or not path.is_file():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "이미지를 찾을 수 없습니다.")
    return path