# app/apis/user_auth_apis.py
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.db.databases import async_get_db
from app.schemas.user import (
    LoginRequest,
    SignupRequest,
    SignupResponse,
    TokenResponse,
)
from app.services import user_auth_service as service

router = APIRouter(prefix="/api/v1/users", tags=["Auth"])


# REQ-USER-001: 회원가입 API
@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=SignupResponse)
def signup(payload: SignupRequest, db: Session = Depends(async_get_db)):
    return service.signup(db, payload)


# REQ-USER-002: 로그인 API
@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(async_get_db)):
    return service.login(db, payload, response)

