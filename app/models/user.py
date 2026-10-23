from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.databases import Base
from app.models.enum import DepartmentEnum, GenderEnum, RoleEnum


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str | None] = mapped_column(String(20), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(
        String(20), unique=True, nullable=True, comment="유저 휴대폰 번호"
    )

    gender: Mapped[GenderEnum] = mapped_column(
        Enum(GenderEnum, name="gender"), nullable=False, comment="성별 선택"
    )

    department: Mapped[DepartmentEnum] = mapped_column(
        Enum(DepartmentEnum, name="department"), nullable=False, comment="부서 선택"
    )
    
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum, name="role"), nullable=False, comment="부여된 역할 권한"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("1"), comment="계정 활성화 여부"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp(), comment="유저 생성 일시"
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, onupdate=func.now(), comment="유저 정보 수정 일시"
    )