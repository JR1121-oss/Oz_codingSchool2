# app/repositories/user_auth_repository.py
# DB에서 이메일/전화번호로 유저를 찾고, 신규 유저를 생성하는 pure SQLAlchemy 쿼리 모듈

from typing import Optional
from sqlalchemy.orm import Session
from app.models.enum import DepartmentEnum, GenderEnum, RoleEnum
from app.models.user import User


def find_user_by_email(db: Session, email: str) -> Optional[User]:
    """이메일로 사용자 조회"""
    return db.query(User).filter(User.email == email).first()


def find_user_by_phone(db: Session, phone: str) -> Optional[User]:
    """전화번호로 사용자 조회"""
    return db.query(User).filter(User.phone_number == phone).first()


def create_user(
    db: Session,
    email: str,
    hashed_password: str,
    name: str,
    department: DepartmentEnum,
    gender: GenderEnum,
    phone_number: str
) -> User:
    """신규 사용자 생성 (기본 권한: PENDING)"""
    new_user = User(
        email=email,
        hashed_password=hashed_password,
        name=name,
        department=department,
        gender=gender,
        phone_number=phone_number,
        role=RoleEnum.PENDING,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user