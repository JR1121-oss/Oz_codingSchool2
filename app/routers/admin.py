# 관리자(Admin) 전용 기능을 담당
# 시스템에 등록된 전체 회원 목록을 조회 or 특정 회원의 권한(Role) or 부서(Department) 정보를 변경하는 API 엔드포인트를 제공
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.deps import get_current_user
from app.models.enum import RoleEnum
from app.models.user import User
from app.schemas.user import UserSignupData  # 회원 정보 응답 DTO
from app.services import user_admin_service

router = APIRouter()


# 관리자 권한 검증 전용 Dependency 함수
async def verify_admin_role(current_user: User = Depends(get_current_user)) -> User:
    """현재 로그인된 사용자가 ADMIN 권한을 가지고 있는지 검증합니다."""
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다.",
        )
    return current_user


@router.get(
    "/users",
    response_model=list[UserSignupData],
    summary="[관리자] 전체 회원 목록 조회",
)
async def get_all_users(
    admin_user: User = Depends(verify_admin_role),
    db: AsyncSession = Depends(async_get_db),
):
    """
    관리자 권한을 가진 사용자만 접근 가능하며,
    전체 회원 목록을 조회하여 반환합니다.
    """
    users = await user_admin_service.get_user_list(db=db)
    return users


@router.patch(
    "/users/{user_id}/role",
    response_model=UserSignupData,
    summary="[관리자] 특정 회원의 권한/부서 변경",
)
async def update_user_role(
    user_id: int,
    new_role: RoleEnum,
    admin_user: User = Depends(verify_admin_role),
    db: AsyncSession = Depends(async_get_db),
):
    """
    특정 회원의 권한(예: USER -> ADMIN)을 변경합니다.
    """
    updated_user = await user_admin_service.change_user_role(
        db=db, target_user_id=user_id, new_role=new_role
    )
    return updated_user