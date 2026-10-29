# app/services/user_me_service.py
# 마이페이지(D) 비즈니스 로직 (REQ-USER-006 ~ 009)
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories import user_me_repository as repo
from app.schemas.user import PasswordUpdateReq, UserUpdateReq


async def update_user_profile(db: AsyncSession, user: User, req: UserUpdateReq) -> User:
    """내 정보 수정 (REQ-USER-007) - 보낸 필드만 반영"""
    update_data = req.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 항목을 하나 이상 입력해야 합니다.",
        )

    new_phone = update_data.get("phone_number")
    if new_phone and await repo.find_other_user_by_phone(db, new_phone, user.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 등록된 전화번호입니다.",
        )

    return await repo.update_user(db, user, update_data)


async def change_password(db: AsyncSession, user: User, req: PasswordUpdateReq) -> None:
    """비밀번호 변경 (REQ-USER-008)"""
    if not verify_password(req.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호가 일치하지 않습니다.",
        )
    if verify_password(req.new_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="새 비밀번호가 현재 비밀번호와 같습니다.",
        )

    await repo.update_user(db, user, {"hashed_password": hash_password(req.new_password)})


async def delete_account(db: AsyncSession, user: User) -> None:
    """회원 탈퇴 (REQ-USER-009)"""
    await repo.delete_user(db, user)