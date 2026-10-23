from sqlalchemy import SmallInt, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.core.db.databases import Base
from app.models.enum import GenderEnum

class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False, comment="환자 성명")
    age: Mapped[int] = mapped_column(SmallInt, nullable=False, comment="smallint")

    # 공통 Enum 적용
    gender: Mapped[GenderEnum] = mapped_column(nullable=False, comment="환자 성별")

    phone: Mapped[str] = mapped_column(String(11), nullable=False, comment="환자 연락처, 국내 전화번호로 한정")

    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="환자 정보 등록 일시"
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=True,
        onupdate=func.current_timestamp(),
        comment="환자 정보 수정 일시"
    )