# app/apis/v1/user_admin_repository.py
from collections.abc import Sequence
from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enum import DepartmentEnum, RoleEnum
from app.models.user import User


async def find_users(
    db: AsyncSession,
    search: Optional[str],
    department: Optional[DepartmentEnum],
) -> Sequence[User]:
    """이메일/이름 부분 일치 검색 + 부서 필터. 조건이 없으면 전체 조회."""
    stmt = select(User).order_by(User.id)

    if search:
        # autoescape=True: 검색어의 %, _ 를 와일드카드가 아닌 일반 문자로 취급
        stmt = stmt.where(
            or_(
                User.email.contains(search, autoescape=True),
                User.name.contains(search, autoescape=True),
            )
        )
    if department:
        stmt = stmt.where(User.department == department)

    result = await db.execute(stmt)
    return result.scalars().all()


async def find_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    return await db.get(User, user_id)


async def save_role(db: AsyncSession, user: User, role: RoleEnum) -> User:
    user.role = role
    await db.commit()
    await db.refresh(user)
    return user