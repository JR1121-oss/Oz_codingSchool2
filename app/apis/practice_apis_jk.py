from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import re

router = APIRouter(prefix="/practice_api", tags=["Part D: Mypage API"])

# 연습용 회원 데이터 리스트
user_list = [
    {
        "id": 1,
        "name": "홍길동",
        "age": 24,
        "email": "gildong24@example.com",
        "password": "Password1234!!",
    },
    {
        "id": 2,
        "name": "장문복",
        "age": 21,
        "email": "moonluck12@example.com",
        "password": "Check1321!",
    },
    {
        "id": 3,
        "name": "임우진",
        "age": 31,
        "email": "limousine33@example.com",
        "password": "lwsPAssword12@",
    },
]

# --- Pydantic 요청 모델 정의 ---
class UserProfileUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=10)
    age: int | None = Field(None, ge=14)

class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=20)

    def validate_password(self):
        if not (re.search(r"[A-Z]", self.new_password) and 
                re.search(r"[a-z]", self.new_password) and 
                re.search(r"[!@#$%^&*(),.?\":{}|<>]", self.new_password)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="새 비밀번호는 대소문자와 특수문자를 각각 1개 이상 포함해야 합니다."
            )


# --- REQ-USER-006: 회원 정보 조회 (기본 1번 사용자 대상) ---
@router.get("/users/me", summary="내 프로필 조회")
def get_my_profile(user_id: int = 1):
    for user in user_list:
        if user["id"] == user_id:
            return {
                "id": user["id"],
                "name": user["name"],
                "age": user["age"],
                "email": user["email"]
            }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다.")


# --- REQ-USER-007: 회원 정보 수정 ---
@router.patch("/users/me", summary="내 프로필 수정")
def update_my_profile(profile_data: UserProfileUpdate, user_id: int = 1):
    for user in user_list:
        if user["id"] == user_id:
            if profile_data.name is not None:
                user["name"] = profile_data.name
            if profile_data.age is not None:
                user["age"] = profile_data.age
            return {
                "message": "프로필이 성공적으로 수정되었습니다.",
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "age": user["age"],
                    "email": user["email"]
                }
            }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다.")


# --- REQ-USER-008: 비밀번호 변경 ---
@router.patch("/users/me/password", summary="비밀번호 변경")
def change_password(pwd_data: PasswordChange, user_id: int = 1):
    pwd_data.validate_password()
    for user in user_list:
        if user["id"] == user_id:
            if user["password"] != pwd_data.old_password:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="현재 비밀번호가 일치하지 않습니다.")
            user["password"] = pwd_data.new_password
            return {"message": "비밀번호가 성공적으로 변경되었습니다."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다.")


# --- REQ-USER-009: 회원 탈퇴 ---
@router.delete("/users/me", summary="회원 탈퇴")
def delete_account(user_id: int = 1):
    for index, user in enumerate(user_list):
        if user["id"] == user_id:
            user_list.pop(index)
            return {"message": "회원 탈퇴가 완료되었습니다."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다.")