from datetime import datetime
from sqlalchemy import BigInteger, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db.databases import Base

class XrayImage(Base):
    __tablename__ = "xray_images"

    id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True, 
        autoincrement=True
    )

    # record_id는 medical_records.id를 외래키로 참조 (삭제 시 CASCADE로 동작)
    record_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("medical_records.id", ondelete="CASCADE"),
        nullable=False,
        comment="진료 기록 id"
    )

    # uploader_id는 users.id를 참조하여 NULL을 허용 (삭제 시 SET NULL로 동작)
    uploader_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True,
        comment="X-ray 이미지를 업로드한 유저의 id"
    )

    image_url: Mapped[str] = mapped_column(
        String(2048), nullable=False, comment="이미지 url"
    )

    shooting_datetime: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="X-ray 촬영일시"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="X-ray 이미지 등록 일시"
    )