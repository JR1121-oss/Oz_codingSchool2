# app/apis/user_admin_apis.py
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.deps import get_current_admin
from app.models.enum import DepartmentEnum as Department
from app.models.user import User
from app.schemas.user import UserAdminResponse, RoleUpdateRequest, RoleUpdateResponse
from app.services import user_admin_service as service

router = APIRouter(prefix="/api/v1/users", tags=["Admin"])


# C 파트: 회원 목록 조회 (ADMIN 전용)
@router.get("", response_model=List[UserAdminResponse])
async def get_users(
    search: Optional[str] = Query(None, max_length=255),
    department: Optional[Department] = Query(None),
    db: AsyncSession = Depends(async_get_db),
    admin: User = Depends(get_current_admin),
):
    return await service.get_users(db, search, department)


# C 파트: 회원 권한 변경 (ADMIN 전용)
@router.patch("/{user_id}/role", response_model=RoleUpdateResponse)
async def update_user_role(
    user_id: int,
    payload: RoleUpdateRequest,
    db: AsyncSession = Depends(async_get_db),
    admin: User = Depends(get_current_admin),
):
    return await service.change_user_role(db, admin, user_id, payload.role)