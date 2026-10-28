# app/apis/user_auth_apis.py
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession   # Session → AsyncSession

from app.core.db.databases import async_get_db
from app.core.security import create_refresh_token, set_refresh_cookie
from app.schemas.user import SignupRequest, SignupResponse, TokenResponse
from app.services import user_auth_service as service

router = APIRouter(prefix="/api/v1/users", tags=["Auth"])


# REQ-USER-001: 회원가입 API
@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=SignupResponse)
async def signup(payload: SignupRequest, db: AsyncSession = Depends(async_get_db)):
    return await service.signup(db, payload)


# REQ-USER-002: 로그인 API
@router.post("/login", response_model=TokenResponse)
async def login( 
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(async_get_db),
):
    # OAuth2 규격상 필드명이 username이지만, 우리 서비스에서는 이메일을 담는다.
    token = await service.login(db, form_data.username, form_data.password)
    set_refresh_cookie(response, create_refresh_token(token.user.id))
    return token
