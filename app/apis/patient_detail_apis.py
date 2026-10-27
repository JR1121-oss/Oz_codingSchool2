# app/apis/patient_detail_apis.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

# 프로젝트 폴더 구조에 맞춘 import 경로 지정
from app.core.db.databases import async_get_db
from app.schemas.patient import PatientUpdateRequest, PatientResponse

router = APIRouter(prefix="/patients", tags=["Patients"])


# REQ-PATIENT-002: 환자 상세 정보 조회 API
@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int, 
    db: AsyncSession = Depends(async_get_db)
):
    """
    환자 PK(patient_id)를 입력받아 상세 정보를 조회합니다.
    """
    
    # Repository 연동
    patient = None
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="환자를 찾을 수 없습니다."
        )
    return patient


# REQ-PATIENT-003: 환자 정보 수정 API
@router.patch("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int, 
    update_data: PatientUpdateRequest, 
    db: AsyncSession = Depends(async_get_db)
):
    """
    환자의 인적사항(이름, 연락처 등) 정보를 선택적으로 수정합니다.
    """

    # Repository 연동
    patient = None
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="환자를 찾을 수 없습니다."
        )
    return patient