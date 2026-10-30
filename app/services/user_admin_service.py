# app/services/user_admin_service.py
from collections.abc import Sequence
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enum import DepartmentEnum, RoleEnum
from app.models.user import User
from app.repositories import user_admin_repository as repo


async def get_users(
    db: AsyncSession,
    search: Optional[str] = None,
    department: Optional[DepartmentEnum] = None,
) -> Sequence[User]:
    return await repo.find_users(db, search, department)


async def change_user_role(
    db: AsyncSession, admin: User, user_id: int, role: RoleEnum
) -> User:
    # 본인 권한 변경 금지 (관리자가 자신의 권한을 낮춰 ADMIN이 없어지는 상황 방지)
    if admin.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="본인의 권한은 변경할 수 없습니다.",
        )

    target = await repo.find_user_by_id(db, user_id)
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 회원입니다.",
        )

    return await repo.save_role(db, target, role)