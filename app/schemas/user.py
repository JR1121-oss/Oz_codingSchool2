# app/schemas/user.py
from pydantic import BaseModel, ConfigDict

from app.models.enum import DepartmentEnum, GenderEnum, RoleEnum


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
