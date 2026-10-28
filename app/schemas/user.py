# app/schemas/user.py
import re
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.models.enum import DepartmentEnum, GenderEnum, RoleEnum

PASSWORD_ERROR_MESSAGE = "비밀번호는 대소문자, 특수문자, 숫자를 각 1개씩 포함한 8자리 이상이어야 합니다."

class SignupRequest(BaseModel):
    """회원가입 요청 본문 (REQ-USER-001)"""
    email: EmailStr
    password: str = Field(..., max_length=64)
    name: str = Field(..., min_length=2, max_length=20)
    department: DepartmentEnum
    gender: GenderEnum
    phone_number: str = Field(..., pattern=r"^\d{11}$")

    @field_validator("password")
    @classmethod
    def check_password(cls, value: str) -> str:
        if (
            len(value) < 8
            or not re.search(r"[A-Z]", value)
            or not re.search(r"[a-z]", value)
            or not re.search(r"\d", value)
            or not re.search(r"[^A-Za-z0-9]", value)
        ):
            raise ValueError(PASSWORD_ERROR_MESSAGE)
        return value


class UserSignupData(BaseModel):
    """회원가입 응답 내 user 객체"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    department: DepartmentEnum
    gender: GenderEnum
    phone_number: str
    role: RoleEnum


class SignupResponse(BaseModel):
    """회원가입 응답 규격"""
    message: str = "회원가입이 완료되었습니다."
    user: UserSignupData


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