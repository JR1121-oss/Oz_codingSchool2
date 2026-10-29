# app/apis/v1/record_detail_apis.py
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.deps import get_approved_user
from app.models.enum import RoleEnum
from app.models.JR_xray_image import XrayImage
from app.models.medical_record import MedicalRecord
from app.models.user import User
from app.schemas.medical_record import MedicalRecordDetailResponse

router = APIRouter()  # prefix 와 tags 는 main.py 가 붙여 준다


@router.get("/{record_id}", response_model=MedicalRecordDetailResponse)
async def get_record(
    record_id: int,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_approved_user),  # 승인된 사용자만 조회 가능
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