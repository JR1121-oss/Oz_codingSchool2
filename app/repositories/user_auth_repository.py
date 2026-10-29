# app/repositories/user_auth_repository.py
# 회원가입·로그인·토큰 재발급에 필요한 사용자 조회/생성 쿼리 모듈 (비동기)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enum import DepartmentEnum, GenderEnum, RoleEnum
from app.models.user import User


async def find_user_by_email(db: AsyncSession, email: str) -> User | None:
    """이메일로 사용자 조회"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def find_user_by_phone(db: AsyncSession, phone: str) -> User | None:
    """전화번호로 사용자 조회"""
    result = await db.execute(select(User).where(User.phone_number == phone))
    return result.scalar_one_or_none()


async def find_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """유저 ID로 사용자 조회 (토큰 재발급 시 사용)"""
    return await db.get(User, user_id)


async def create_user(
    db: AsyncSession,
    email: str,
    hashed_password: str,
    name: str,
    department: DepartmentEnum,
    gender: GenderEnum,
    phone_number: str,
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
        is_active=True,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
