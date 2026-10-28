# app/core/security.py
from datetime import datetime, timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Response
from app.core.config import settings

# 환경변수 설정
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
REFRESH_COOKIE_NAME = "refresh_token"

# 로컬 HTTP 개발 환경에서는 COOKIE_SECURE=false로 설정
COOKIE_SECURE = settings.COOKIE_SECURE
COOKIE_SAMESITE = "lax"

_ph = PasswordHasher()


# ---------- 비밀번호 해싱 및 검증 (A 파트) ----------
def hash_password(password: str) -> str:
    """비밀번호를 해싱합니다."""
    return _ph.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """입력된 비밀번호와 해시된 비밀번호가 일치하는지 검증합니다."""
    try:
        return _ph.verify(hashed_password, password)
    except VerifyMismatchError:
        return False


# ---------- JWT 토큰 생성 및 디코딩 (A & B 파트 공통) ----------
def _create_token(user_id: int, token_type: str, expires_delta: timedelta) -> str:
    """내부 토큰 생성 헬퍼 함수"""
    payload = {
        "sub": str(user_id),  # PyJWT는 sub가 문자열이어야 합니다.
        "type": token_type,   # "access" 또는 "refresh"
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(user_id: int) -> str:
    """Access Token을 발급합니다. (유효기간: 30분)"""
    return _create_token(
        user_id, 
        token_type="access", 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )


def create_refresh_token(user_id: int) -> str:
    """Refresh Token을 발급합니다. (유효기간: 7일)"""
    return _create_token(
        user_id, 
        token_type="refresh", 
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )


def decode_token(token: str, expected_type: str) -> int:
    """
    토큰을 디코딩하고 타입을 검증합니다.
    유효성 검사 성공 시 user_id(int)를 반환합니다.
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    # 토큰 타입(access / refresh) 일치 여부 확인
    if payload.get("type") != expected_type:
        raise ValueError("token type mismatch")
    return int(payload["sub"])


# ---------- 리프레시 토큰 쿠키 제어 (A & B 파트) ----------
def set_refresh_cookie(response: Response, token: str) -> None:
    """로그인 시 refresh_token 쿠키를 설정합니다. (A 파트)"""
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # 7일 (초 단위)
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
    )


def clear_refresh_cookie(response: Response) -> None:
    """로그아웃 시 refresh_token 쿠키를 만료(Max-Age=0)시킵니다. (B 파트)"""
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
    )
