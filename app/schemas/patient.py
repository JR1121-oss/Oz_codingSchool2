# app/schemas/patient.py
# 환자 등록·조회·수정 API 요청/응답 Pydantic 스키마 (REQ-PTNT-001 ~ 004)
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enum import GenderEnum


class PatientCreate(BaseModel):
    """환자 등록 요청 (REQ-PTNT-001)
    patient_list_apis.py에서 Patient(**model_dump())로 넘기므로 필드명 = 모델 속성명이어야 한다.
    """

    name: str = Field(..., min_length=1, max_length=30, description="환자 성명")
    age: int = Field(..., ge=0, le=150, description="환자 나이")
    gender: GenderEnum = Field(..., description="환자 성별 (male / female)")
    phone_number: str = Field(..., pattern=r"^\d{10,11}$", description="숫자만 10~11자리")


class PatientUpdateRequest(BaseModel):
    """환자 정보 수정 요청 (REQ-PTNT-004) - 보낸 필드만 수정 (이름, 연락처)"""

    name: str | None = Field(None, min_length=1, max_length=30)
    phone_number: str | None = Field(None, pattern=r"^\d{10,11}$")


class PatientResponse(BaseModel):
    """환자 등록/목록/상세/수정 공통 응답 (REQ-PTNT-001 ~ 004)"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    age: int
    gender: GenderEnum
    phone_number: str
    created_at: datetime
    updated_at: datetime | None = None