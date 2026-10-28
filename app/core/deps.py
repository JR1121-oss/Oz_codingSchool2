# app/core/deps.py
# deps = dependencies(의존성들)의 줄임말 -> API 요청이 실행되기 전에 먼저 처리해야 하는 공통 로직을 한곳에 모아둔 파일
# FastAPI에서는 의존성 주입(Dependency Injection) 시스템인 Depends() 기능을 핵심적으로 사용
# (예: JWT 토큰을 검증해 현재 로그인한 유저를 찾아오기, DB 세션 연결하기, 권한 체크하기 등)

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import decode_token 
from app.core.db.databases import async_get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(async_get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않거나 만료된 토큰입니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = decode_token(token, expected_type="access") # 만료·서명·타입 검증
    except (jwt.InvalidTokenError, ValueError, KeyError):
        raise credentials_exception

    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_exception
    return user
