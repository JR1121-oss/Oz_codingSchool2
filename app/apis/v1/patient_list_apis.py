# app/apis/v1/patient_list_apis.py
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.deps import get_approved_user, get_medical_user
from app.models.enum import GenderEnum
from app.models.patient import Patient
from app.models.user import User
from app.schemas.patient import PatientCreate, PatientResponse

# prefix는 main.py에서 "/api/v1/patients"로 지정하므로 여기서는 비워둔다.
router = APIRouter()


# REQ-PTNT-001: 환자 정보 등록 API / 권한: 의료진 부서 + 승인된 사용자
@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    payload: PatientCreate,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_medical_user),
):
    """
    이름, 나이, 성별, 연락처를 입력받아 환자를 신규 등록합니다.
    id, created_at은 DB에서 자동으로 채워집니다.
    """
    patient = Patient(**payload.model_dump())
    db.add(patient)
    await db.commit()
    await db.refresh(patient)  # DB가 채운 id, created_at 값을 다시 읽어온다.
    return patient


# REQ-PTNT-002: 환자 목록 조회 API / 권한: 개발진 / 의료진 / 연구진 중 승인된 사용자 (PENDING은 403)
@router.get("", response_model=list[PatientResponse])
async def get_patients(
    name: Optional[str] = Query(None, description="이름 부분 일치 검색"),
    gender: Optional[GenderEnum] = Query(None, description="성별 필터 (male / female)"),
    min_age: Optional[int] = Query(None, ge=0, description="최소 나이"),
    max_age: Optional[int] = Query(None, ge=0, description="최대 나이"),
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_approved_user),
):
    """
    등록된 환자 목록을 조회합니다.
    이름 검색, 성별 필터, 나이 범위 필터를 함께 사용할 수 있습니다.
    """
    if min_age is not None and max_age is not None and min_age > max_age:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="최소 나이는 최대 나이보다 클 수 없습니다.",
        )

    stmt = select(Patient)

    if name:
        stmt = stmt.where(Patient.name.ilike(f"%{name}%"))
    if gender:
        stmt = stmt.where(Patient.gender == gender)
    if min_age is not None:
        stmt = stmt.where(Patient.age >= min_age)
    if max_age is not None:
        stmt = stmt.where(Patient.age <= max_age)

    stmt = stmt.order_by(Patient.id.desc())  # 최근 등록한 환자가 위로

    result = await db.execute(stmt)
    return result.scalars().all()
