# app/schemas/user.py
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.enum import DepartmentEnum, GenderEnum, RoleEnum


class SignupRequest(BaseModel):
    """회원가입 요청 본문 (REQ-USER-001)"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
    name: str = Field(..., min_length=2, max_length=20)
    department: DepartmentEnum
    gender: GenderEnum
    phone: str = Field(..., pattern=r"^\d{11}$")


class UserSignupData(BaseModel):
    """회원가입 응답 내 user 객체"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    department: DepartmentEnum
    gender: GenderEnum
    phone: str = Field(..., validation_alias="phone_number")
    role: RoleEnum


class SignupResponse(BaseModel):
    """회원가입 응답 규격"""
    message: str = "회원가입이 완료되었습니다."
    user: UserSignupData


class LoginRequest(BaseModel):
    """로그인 요청 본문 (REQ-USER-002)"""
    email: EmailStr
    password: str


class LoginUserData(BaseModel):
    """로그인 응답 내 user 객체"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    role: RoleEnum


class TokenResponse(BaseModel):
    """A & B 파트 공통 토큰 응답 규격"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800
    user: LoginUserData

# 사용자 정보 수정 요청(PATCH /me) 시 클라이언트가 보낼 수정 데이터 규격 클래스 추가
class UserUpdateReq(BaseModel):
    """현재 로그인된 사용자 정보 수정 요청 본문 (REQ-USER-004)"""
    name: str | None = Field(None, min_length=2, max_length=20)
    password: str | None = Field(None, min_length=8, max_length=64)
    phone: str | None = Field(None, pattern=r"^\d{11}$")
