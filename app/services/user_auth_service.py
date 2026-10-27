# app/services/user_auth_service.py
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories import user_auth_repository as repo
from app.schemas.user import LoginRequest, LoginUserData, SignupRequest, TokenResponse


async def register_user(db: AsyncSession, req: SignupRequest) -> User:
    """회원가입 (REQ-USER-001)"""
    # 1. 이메일 중복 확인
    if await repo.find_user_by_email(db, req.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 가입된 이메일입니다.",
        )

    # 2. 전화번호 중복 확인
    if await repo.find_user_by_phone(db, req.phone_number):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 등록된 전화번호입니다.",
        )

    # 3. 비밀번호 해싱 후 생성
    return await repo.create_user(
        db=db,
        email=req.email,
        hashed_password=hash_password(req.password),
        name=req.name,
        department=req.department,
        gender=req.gender,
        phone_number=req.phone_number,
    )


async def authenticate_user(db: AsyncSession, req: LoginRequest) -> TokenResponse:
    """로그인 (REQ-USER-002) - Refresh Token 쿠키는 라우터에서 설정"""
    # 1. 이메일 조회 및 비밀번호 검증
    user = await repo.find_user_by_email(db, req.email)
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 일치하지 않습니다.",
        )

    # 2. 계정 활성화 여부 확인
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 사용자입니다.",
        )

    # 3. Access Token 발급
    return TokenResponse(
        access_token=create_access_token(user_id=user.id),
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=LoginUserData.model_validate(user),
    )
