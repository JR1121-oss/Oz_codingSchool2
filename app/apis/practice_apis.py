# app/apis/practice_apis.py
import re
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator

router = APIRouter()

# 과제 기본 데이터[cite: 10]
user_list = [
    {"id": 1, "name": "홍길동", "age": 24, "email": "gildong24@example.com", "password": "Password1234!!"},
    {"id": 2, "name": "장문복", "age": 21, "email": "moonluck12@example.com", "password": "Check1321!"},
    {"id": 3, "name": "임우진", "age": 31, "email": "limousine33@example.com", "password": "lwsPAssword12@"}
]

# 공통 응답 Pydantic 모델 (password 제외)
class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    email: str


# --- 3번/4번 요구사항: 유효성 검증 유틸 및 Pydantic 모델 ---[cite: 10, 11]
EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

def validate_password(value: str) -> str:
    if not 8 <= len(value) <= 20:
        raise ValueError("비밀번호는 8자 이상 20자 이하여야 합니다.")
    if not re.search(r"[A-Z]", value):
        raise ValueError("비밀번호에는 대문자가 1개 이상 필요합니다.")
    if not re.search(r"[a-z]", value):
        raise ValueError("비밀번호에는 소문자가 1개 이상 필요합니다.")
    if not re.search(r"[^A-Za-z0-9\s]", value):
        raise ValueError("비밀번호에는 특수문자가 1개 이상 필요합니다.")
    return value

def validate_email(value: str) -> str:
    if len(value) > 30:
        raise ValueError("이메일은 30자 이하여야 합니다.")
    if not EMAIL_PATTERN.match(value):
        raise ValueError("이메일 형식이 올바르지 않습니다.")
    return value

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=10)
    age: int = Field(..., ge=14)
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def check_email(cls, value):
        return validate_email(value)

    @field_validator("password")
    @classmethod
    def check_password(cls, value):
        return validate_password(value)

class UserUpdate(BaseModel):
    age: Optional[int] = Field(default=None, ge=14)
    email: Optional[str] = None
    password: Optional[str] = None

    @field_validator("email")
    @classmethod
    def check_email(cls, value):
        return value if value is None else validate_email(value)

    @field_validator("password")
    @classmethod
    def check_password(cls, value):
        return value if value is None else validate_password(value)


# ----------------------------------------------------
# [1번 요구사항] 모든 회원 목록 조회 API[cite: 10]
# ----------------------------------------------------
@router.get("/practice_api/users", response_model=List[UserResponse])
def get_users():
    return user_list


# ----------------------------------------------------
# [2번 요구사항] 특정 회원 조회 API[cite: 10]
# ----------------------------------------------------
@router.get("/practice_api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    for u in user_list:
        if u["id"] == user_id:
            return u
    raise HTTPException(status_code=404, detail="Not Found")


# ----------------------------------------------------
# [3번 요구사항] 회원 정보 추가 API[cite: 10]
# ----------------------------------------------------
@router.post("/practice_api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate):
    if any(u["email"] == body.email for u in user_list):
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")

    new_id = max([u["id"] for u in user_list], default=0) + 1
    new_user = {
        "id": new_id,
        "name": body.name,
        "age": body.age,
        "email": body.email,
        "password": body.password,
    }
    user_list.append(new_user)
    return new_user


# ----------------------------------------------------
# [4번 요구사항] 회원 정보 수정 API[cite: 11]
# ----------------------------------------------------
@router.patch("/practice_api/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, body: UserUpdate):
    user = next((u for u in user_list if u["id"] == user_id), None)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="존재하지 않는 회원입니다.")

    if body.age is None and body.email is None and body.password is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="수정할 항목을 하나 이상 입력해야 합니다.")

    if body.email is not None and any(u["email"] == body.email and u["id"] != user_id for u in user_list):
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")

    if body.age is not None:
        user["age"] = body.age
    if body.email is not None:
        user["email"] = body.email
    if body.password is not None:
        user["password"] = body.password

    return user


# ----------------------------------------------------
# [5번 요구사항] 회원 정보 삭제 API[cite: 11]
# ----------------------------------------------------
@router.delete("/practice_api/users/{user_id}")
def delete_user(user_id: int):
    for idx, user in enumerate(user_list):
        if user["id"] == user_id:
            del user_list[idx]
            return {"message": f"User {user_id}가 성공적으로 삭제되었습니다."}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User Not Found"
    )