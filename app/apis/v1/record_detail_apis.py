# app/apis/v1/record_detail_apis.py
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.deps import get_current_user
from app.models.enum import RoleEnum
from app.models.JR_xray_image import XrayImage
from app.models.medical_record import MedicalRecord
from app.models.user import User

router = APIRouter()  # prefix 와 tags 는 main.py 가 붙여 준다


class MedicalRecordDetailResponse(BaseModel):
    """진료기록 상세 조회 응답 (REQ-MDR-003)"""

    id: int                        # 진료 기록 ID
    patient_id: int                # 환자 상세 페이지로 돌아갈 때 필요하면 사용 (프론트가 안 쓰면 삭제)
    chart_number: str              # 차트 넘버
    symptoms: str                  # 증상
    xray_image_url: str | None     # 흉부 X-Ray 이미지 (이미지가 없으면 null)
    created_at: datetime           # 생성일시


@router.get("/{record_id}", response_model=MedicalRecordDetailResponse)
async def get_record(
    record_id: int,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user),  # 로그인한 사용자만 조회 가능
):
    # 1. 권한 확인: STAFF, ADMIN 만 허용 (PENDING 은 접근 불가)
    if current_user.role not in (RoleEnum.STAFF, RoleEnum.ADMIN):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "접근 권한이 없습니다.")

    # 2. 진료기록 조회
    record = await db.scalar(select(MedicalRecord).where(MedicalRecord.id == record_id))
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "진료 기록을 찾을 수 없습니다.")

    # 3. X-Ray 이미지 조회: 한 진료기록에 여러 장이면 가장 최근 1장
    #    (record.xray_images 로 읽으면 비동기 세션에서 에러가 나므로 따로 조회한다)
    xray_image_url = await db.scalar(
        select(XrayImage.image_url)
        .where(XrayImage.record_id == record_id)
        .order_by(XrayImage.created_at.desc(), XrayImage.id.desc())
        .limit(1)
    )

    return MedicalRecordDetailResponse(
        id=record.id,
        patient_id=record.patient_id,
        chart_number=record.chart_number,
        symptoms=record.symptoms,
        xray_image_url=xray_image_url,
        created_at=record.created_at,
    )