from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import re

router = APIRouter(prefix="/practice_api")

# 초기 제공되는 회원 리스트 데이터
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

# --- 3번 API를 위한 Pydantic 데이터 검증 모델 정의 ---
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=10) # 이름: 최소 2글자, 최대 10글자
    age: int = Field(..., ge=14)                          # 나이: 최소 14세 이상
    email: str = Field(..., max_length=30)                # 이메일: 최대 30자
    password: str = Field(..., min_length=8, max_length=20) # 비밀번호: 최소 8자, 최대 20자

    def validate_custom_fields(self):
        # 1. 이메일 정규표현식 검증
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, self.email):
            raise HTTPException(status_code=400, detail="올바른 이메일 형식이 아닙니다.")
        
        # 2. 이메일 중복 불가능 검증
        for user in user_list:
            if user["email"] == self.email:
                raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")

        # 3. 비밀번호 대소문자, 특수문자 각 1개씩 필수 검증
        if not (re.search(r"[A-Z]", self.password) and 
                re.search(r"[a-z]", self.password) and 
                re.search(r"[!@#$%^&*(),.?\":{}|<>]", self.password)):
            raise HTTPException(status_code=400, detail="비밀번호는 대소문자와 특수문자를 각각 1개 이상 포함해야 합니다.")


# --- 3. 새로운 회원을 추가하는 API ---
@router.post(
    "/users",
    summary="회원 정보 추가 API"
)
def create_user(user_data: UserCreate):
    # 커스텀 유효성 검사 실행 (오타 수정 완료: validate)
    user_data.validate_custom_fields()

    # id는 자동으로 1씩 증가
    new_id = max([u["id"] for u in user_list], default=0) + 1
    
    # 딕셔너리 생성 (변수명 오타 수정 완료: user_data)
    new_user = {
        "id": new_id,
        "name": user_data.name,
        "age": user_data.age,
        "email": user_data.email,
        "password": user_data.password
    }
    user_list.append(new_user)
    
    return {
        "message": "User created successfully", 
        "user": {
            "id": new_user["id"],
            "name": new_user["name"],
            "age": new_user["age"],
            "email": new_user["email"]
        }
    }
