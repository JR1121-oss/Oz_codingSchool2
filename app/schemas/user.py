# app/schemas/user.py
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.models.enum import DepartmentEnum, GenderEnum, RoleEnum
import re

# 프론트(apis.js)가 이 문구를 그대로 찾아서 표시하므로 수정 시 함께 변경해야 함
PASSWORD_ERROR_MESSAGE = "비밀번호는 대소문자, 특수문자, 숫자를 각 1개씩 포함한 8자리 이상이어야 합니다."

def validate_password_rule(value: str) -> str:
    if not (
        re.search(r"[A-Z]", value)
        and re.search(r"[a-z]", value)
        and re.search(r"\d", value)
        and re.search(r"[^A-Za-z0-9]", value)
    ):
        raise ValueError(PASSWORD_ERROR_MESSAGE)
    return value

# pages.js의 회원가입 코드 -> phone_number: document ... 이렇게 JSON 만듦.
class SignupRequest(BaseModel):
    """회원가입 요청 본문 (REQ-USER-001)"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
    name: str = Field(..., min_length=2, max_length=20)
    department: DepartmentEnum
    gender: GenderEnum
    phone_number: str = Field(..., pattern=r"^\d{11}$")


class UserSignupData(BaseModel):
    """회원가입 응답 내 user 객체"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    department: DepartmentEnum
    gender: GenderEnum
    phone_number: str = Field(..., validation_alias="phone_number")
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
    """로그인 응답 내 정보 조회 응답 (비밀번호 제외)"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    role: RoleEnum
    # 밑에 내용 추가
    department: DepartmentEnum
    gender: GenderEnum
    phone_number: str


class TokenResponse(BaseModel):
    """A & B 파트 공통 토큰 응답 규격"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800
    user: LoginUserData | None = None

# 사용자 정보 수정 요청(PATCH /me) 시 클라이언트가 보낼 수정 데이터 규격 클래스 추가
class UserUpdateReq(BaseModel):
    """현재 로그인된 사용자 정보 수정 요청 본문 (REQ-USER-004)"""
    name: str | None = Field(None, min_length=2, max_length=20)
    phone_number: str | None = Field(None, pattern=r"^\d{11}$")
    # 프론트 마이페이지는 부서와 전화번호만 수정함 (비밀번호는 별도 API)


# ---------- 관리자 API (REQ-USER-004, 005) ----------
class UserAdminResponse(BaseModel):
    """회원 목록 조회 응답 항목 (REQ-USER-004). 비밀번호 관련 값은 포함하지 않는다.

    DB(users)는 email/name/phone_number가 NULL 허용이지만, 회원가입 API에서 필수로
    검증하므로 API 응답에서는 NULL을 허용하지 않는다. (DB는 그대로 두고 API에서 막는다)
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    department: DepartmentEnum
    gender: GenderEnum
    phone_number: str
    is_active: bool
    role: RoleEnum


class RoleUpdateRequest(BaseModel):
    """회원 권한 변경 요청 본문 (REQ-USER-005)"""

    role: RoleEnum


class RoleUpdateResponse(BaseModel):
    """회원 권한 변경 응답"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    role: RoleEnum
