# app/apis/v1/record_list_apis.py
import asyncio
import os
import shutil
from datetime import datetime

from fastapi import APIRouter, File, Form, UploadFile

from app.core.db.databases import IMAGE_DIR, get_next_record_id, records_db

router = APIRouter()


def _save_upload(file_obj, path: str) -> None:
    """파일 저장(동기 I/O). 이벤트 루프를 막지 않도록 스레드에서 실행한다."""
    with open(path, "wb") as f:
        shutil.copyfileobj(file_obj, f)


def _shorten(text: str, limit: int = 100) -> str:
    """증상이 limit자를 넘으면 limit자까지만 보여주고 '...'을 붙인다. (원본은 바꾸지 않음)"""
    return text[:limit] + "..." if len(text) > limit else text


@router.post("/{patient_id}/records", status_code=201)
async def create_medical_record(
    patient_id: int,
    chart_number: str = Form(...),
    symptom: str = Form(...),
    xray_image: UploadFile = File(...),
):
    record_id = get_next_record_id()
    filename = os.path.basename(xray_image.filename or "image")  # ../ 등 경로 문자 제거
    file_location = f"{IMAGE_DIR}/{record_id}_{filename}"

    await asyncio.to_thread(_save_upload, xray_image.file, file_location)

    new_record = {
        "id": record_id,
        "patient_id": patient_id,
        "chart_number": chart_number,
        "symptom": symptom,
        "xray_image_path": file_location,
        "created_at": datetime.now(),
    }
    records_db.append(new_record)
    return new_record


@router.get("/{patient_id}/records")
async def get_patient_records(patient_id: int):
    return [
        {**r, "symptom": _shorten(r["symptom"])}
        for r in records_db
        if r["patient_id"] == patient_id
    ]