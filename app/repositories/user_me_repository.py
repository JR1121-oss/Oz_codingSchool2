# app/repositories/user_me_repository.py
# 마이페이지(D) 관련 사용자 수정/삭제 쿼리 모듈 (비동기)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def find_other_user_by_phone(db: AsyncSession, phone_number: str, exclude_user_id: int) -> User | None:
    """본인을 제외하고 같은 전화번호를 쓰는 사용자 조회"""
    result = await db.execute(
        select(User).where(User.phone_number == phone_number, User.id != exclude_user_id)
    )
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, user: User, update_data: dict) -> User:
    """전달된 필드만 반영하여 저장"""
    for field, value in update_data.items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User) -> None:
    """사용자 삭제 (업로드한 X-Ray의 uploader_id는 FK ON DELETE SET NULL로 비워짐)"""
    await db.delete(user)
    await db.commit()