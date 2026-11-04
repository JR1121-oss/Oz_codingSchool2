# app/apis/v1/medical_record_list_apis.py
# [Presentation] 진료기록 등록 / 환자별 목록 엔드포인트 (REQ-MDR-001, 002)
# 요청을 받아 service를 호출하고 결과를 반환만 한다. 로직은 services/medical_record_service.py
#
# 프론트(static/apis.js) 호출 경로에 맞추기 위해 라우터를 2개로 나눈다. prefix는 main.py에서 붙인다.
#   router                 → prefix "/api/v1/medical-records"  (진료기록 등록)
#   patient_records_router → prefix "/api/v1/patients"         (환자별 진료기록 목록)
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.deps import get_approved_user, get_medical_user
from app.models.user import User
from app.schemas.medical_record import MedicalRecordDetailResponse, MedicalRecordListItem
from app.services import medical_record_service as service

router = APIRouter()
patient_records_router = APIRouter()


# REQ-MDR-001: 진료기록 등록 (승인된 의료진만)
# 최종 경로: POST /api/v1/medical-records  (patient_id는 프론트가 FormData로 보냄)
@router.post(
    "",
    response_model=MedicalRecordDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_medical_record(
    patient_id: int = Form(...),
    chart_number: str = Form(..., max_length=50),
    symptoms: str = Form(...),
    xray_image: UploadFile = File(...),
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_medical_user),
):
    return await service.create_medical_record(
        db,
        patient_id=patient_id,
        chart_number=chart_number,
        symptoms=symptoms,
        xray_image=xray_image,
        uploader_id=current_user.id,
    )


# REQ-MDR-002: 환자별 진료기록 목록 (승인된 사용자)
# 최종 경로: GET /api/v1/patients/{patient_id}/medical-records
@patient_records_router.get(
    "/{patient_id}/medical-records", response_model=list[MedicalRecordListItem]
)
async def get_patient_records(
    patient_id: int,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_approved_user),
):
    return await service.get_patient_records(db, patient_id)