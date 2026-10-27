# app/schemas/patient.py 

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 환자 정보 수정 요청 스키마 (PATCH 요청 시 사용)
class PatientUpdate(BaseModel):
    name: Optional[str] = None
    contact: Optional[str] = None

# 환자 정보 응답 스키마
class PatientResponse(BaseModel):
    id: int
    name: str
    contact: str
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True