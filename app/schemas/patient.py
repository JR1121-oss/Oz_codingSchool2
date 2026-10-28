# app/core/deps.py
# deps = dependencies(의존성들)의 줄임말 -> API 요청이 실행되기 전에 먼저 처리해야 하는 공통 로직을 한곳에 모아둔 파일
# FastAPI에서는 의존성 주입(Dependency Injection) 시스템인 Depends() 기능을 핵심적으로 사용
# (예: JWT 토큰을 검증해 현재 로그인한 유저를 찾아오기, DB 세션 연결하기, 권한 체크하기 등)

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.security import decode_token
from app.models.enum import DepartmentEnum, RoleEnum
from app.models.user import User

# Swagger(/docs)의 Authorize 버튼이 로그인 요청을 보낼 경로 (실제 로그인 API 경로와 같아야 함)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


# 1단계: 토큰 검증 → user_id 반환
async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    Access Token을 검증하고 토큰 안의 user_id를 반환합니다.
    - 서명이 틀리거나 만료된 토큰 → 401
    - refresh 토큰으로 호출한 경우 → 401
    기존 코드와의 호환을 위해 user_id는 문자열로 반환합니다.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않거나 만료된 토큰입니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = decode_token(token, expected_type="access")
    except (jwt.PyJWTError, ValueError, KeyError):
        raise credentials_exception

    return str(user_id)


# 2단계: DB에서 유저 조회 + 승인 여부 확인 → User 반환
async def get_approved_user(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
) -> User:
    """
    로그인했고, 승인(STAFF/ADMIN)된 활성 사용자만 통과시킵니다.
    - 존재하지 않거나 비활성(탈퇴) 사용자 → 401
    - 승인 대기(PENDING) 사용자 → 403
    """
    user = await db.get(User, int(user_id))

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 사용자입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.role == RoleEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="승인 대기 중인 사용자입니다. 관리자의 승인 이후에 사용 가능합니다.",
        )

    return user


# 3단계: 역할/부서별 권한 확인
async def get_medical_user(user: User = Depends(get_approved_user)) -> User:
    """승인된 사용자 중 의료진 부서만 통과시킵니다. (환자 등록, 진료기록 등록 등)"""
    if user.department != DepartmentEnum.MEDICAL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="의료진만 사용할 수 있는 기능입니다.",
        )
    return user


async def get_admin_user(user: User = Depends(get_approved_user)) -> User:
    """관리자(ADMIN)만 통과시킵니다. (회원 목록 조회, 권한 변경 등)"""
    if user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다.",
        )
    return user
