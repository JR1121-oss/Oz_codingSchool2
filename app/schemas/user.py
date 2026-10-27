from pydantic import BaseModel

class TokenResponse(BaseModel):
    """액세스 토큰 재발급 및 로그인 성공 시 반환되는 응답 DTO"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30분 (초 단위)