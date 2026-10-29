# app/services/user_auth_service.py
# 회원가입(A) · 로그인(A) · 토큰 재발급(B) 비즈니스 로직
import jwt
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories import user_auth_repository as repo
from app.schemas.user import LoginRequest, LoginUserData, SignupRequest, TokenResponse


async def register_user(db: AsyncSession, req: SignupRequest) -> User:
    """회원가입 (REQ-USER-001)"""
    if await repo.find_user_by_email(db, req.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 가입된 이메일입니다.",
        )

    if await repo.find_user_by_phone(db, req.phone_number):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 등록된 전화번호입니다.",
        )

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
    user = await repo.find_user_by_email(db, req.email)
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 일치하지 않습니다.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 사용자입니다.",
        )

    return TokenResponse(
        access_token=create_access_token(user_id=user.id),
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=LoginUserData.model_validate(user),
    )


async def refresh_access_token(db: AsyncSession, refresh_token: str | None) -> TokenResponse:
    """토큰 재발급 (NFR-USER-001) - 리프레시 토큰 검증 후 새 액세스 토큰 발급"""
    invalid_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="리프레시 토큰이 유효하지 않거나 만료되었습니다. 다시 로그인해주세요.",
    )

    if not refresh_token:
        raise invalid_exception

    try:
        user_id = decode_token(refresh_token, expected_type="refresh")
    except (jwt.PyJWTError, ValueError, KeyError):
        raise invalid_exception

    user = await repo.find_user_by_id(db, user_id)
    if user is None:
        raise invalid_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 사용자입니다.",
        )

    # 리프레시 토큰은 재발급하지 않음
    return TokenResponse(
        access_token=create_access_token(user_id=user.id),
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
