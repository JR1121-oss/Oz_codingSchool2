# app/services/user_auth_service.py
from fastapi import HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    set_refresh_cookie,
    verify_password,
)
from app.repositories import user_auth_repository as repo
from app.schemas.user import (
    LoginRequest,
    SignupRequest,
    SignupResponse,
    TokenResponse,
)

def signup(db: Session, payload: SignupRequest) -> SignupResponse:
    # 1. 이메일 중복 확인 (409 Conflict)
    if repo.find_user_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 가입된 이메일입니다."
        )

    # 2. 전화번호 중복 확인 (409 Conflict)
    if repo.find_user_by_phone(db, payload.phone):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 등록된 전화번호입니다."
        )

    # 3. 비밀번호 argon2 해싱
    hashed_pwd = hash_password(payload.password)

    # 4. DB 사용자 생성
    user = repo.create_user(
        db=db,
        email=payload.email,
        hashed_password=hashed_pwd,
        name=payload.name,
        department=payload.department,
        gender=payload.gender,
        phone_number=payload.phone
    )

    return SignupResponse(
        message="회원가입이 완료되었습니다.",
        user=user
    )


def login(db: Session, payload: LoginRequest, response: Response) -> TokenResponse:
    # 1. 이메일 조회 및 비밀번호 검증 (401 Unauthorized)
    user = repo.find_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 일치하지 않습니다."
        )

    # 2. 계정 활성화 여부 확인 (403 Forbidden)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 사용자입니다."
        )

    # 3. JWT 토큰 발급
    access_token = create_access_token(user_id=user.id)
    refresh_token = create_refresh_token(user_id=user.id)

    # 4. 공통 헬퍼 함수로 refresh_token 쿠키 설정 (HttpOnly, SameSite, Secure)
    set_refresh_cookie(response, refresh_token)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=1800,
        user=user
    )
