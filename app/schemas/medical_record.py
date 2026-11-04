# app/schemas/medical_record.py
# 진료기록 등록·목록·상세 조회 API 응답 Pydantic 스키마 (REQ-MDR-001 ~ 003)
# 등록 요청은 X-Ray 파일 업로드 때문에 JSON이 아닌 Form으로 받으므로 요청 스키마는 두지 않는다.
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

SYMPTOMS_PREVIEW_LIMIT = 100


class MedicalRecordListItem(BaseModel):
    """환자별 진료기록 목록 항목 (REQ-MDR-002) - 증상은 100자까지만 표시"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    chart_number: str
    symptoms: str
    created_at: datetime

    @field_validator("symptoms")
    @classmethod
    def shorten_symptoms(cls, value: str) -> str:
        # 응답에서만 줄이고 DB 원본은 바꾸지 않는다
        if len(value) > SYMPTOMS_PREVIEW_LIMIT:
            return value[:SYMPTOMS_PREVIEW_LIMIT] + "..."
        return value


class MedicalRecordDetailResponse(BaseModel):
    """진료기록 상세 조회 / 등록 응답 (REQ-MDR-001, 003)"""

    id: int
    patient_id: int                # 프론트 '진료 목록으로' 버튼이 환자 상세로 돌아갈 때 사용
    chart_number: str
    symptoms: str
    xray_image_url: str | None     # 이미지가 없으면 null
    created_at: datetime