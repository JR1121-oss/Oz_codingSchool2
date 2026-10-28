# app/apis/patient_list_apis.py
from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime
# 공통 DB 및 스키마 임포트 (경로는 프로젝트 구조에 맞게 수정)
from app.core.database import patients_db, get_next_patient_id
from app.schemas.patient import PatientCreate

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.post("/", status_code=201)
def create_patient(patient: PatientCreate):
    new_patient = patient.model_dump()
    new_patient.update({
        "id": get_next_patient_id(),
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    })
    patients_db.append(new_patient)
    return new_patient

@router.get("/")
def get_patients(
    name: Optional[str] = Query(None, description="이름 기준 검색"),
    gender: Optional[str] = Query(None, description="성별 필터링"),
    min_age: Optional[int] = Query(None, description="최소 나이"),
    max_age: Optional[int] = Query(None, description="최대 나이")
):
    result = patients_db
    if name:
        result = [p for p in result if name in p["name"]]
    if gender:
        result = [p for p in result if p["gender"] == gender]
    if min_age is not None:
        result = [p for p in result if p["age"] >= min_age]
    if max_age is not None:
        result = [p for p in result if p["age"] <= max_age]
    return result