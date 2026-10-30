# app/apis/v1/user_me_apis.py
# 마이페이지(D) API - prefix "/api/v1/users"는 main.py에서 붙인다
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.deps import get_current_active_user
from app.core.security import clear_refresh_cookie
from app.models.user import User
from app.schemas.user import LoginUserData, PasswordUpdateReq, UserUpdateReq
from app.services import user_me_service as service

router = APIRouter()


# REQ-USER-006: 내 정보 조회 (승인 대기 사용자도 조회 가능해야 프론트가 대기 화면을 보여줌)
@router.get("/me", response_model=LoginUserData, summary="내 정보 조회")
async def get_my_info(current_user: User = Depends(get_current_active_user)):
    return current_user


# REQ-USER-007: 내 정보 수정 (부서, 전화번호)
@router.patch("/me", response_model=LoginUserData, summary="내 정보 수정")
async def update_my_info(
    req: UserUpdateReq,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(async_get_db),
):
    return await service.update_user_profile(db, current_user, req)


# REQ-USER-008: 비밀번호 변경
@router.patch("/me/password", summary="비밀번호 변경")
async def change_my_password(
    req: PasswordUpdateReq,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(async_get_db),
):
    await service.change_password(db, current_user, req)
    return {"message": "비밀번호가 변경되었습니다."}


# REQ-USER-009: 회원 탈퇴 - 탈퇴 후 refresh 쿠키도 지운다
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT, summary="회원 탈퇴")
async def delete_my_account(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(async_get_db),
):
    await service.delete_account(db, current_user)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    clear_refresh_cookie(response)
    return response