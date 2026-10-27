import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, decode_token
from app.repositories.user_auth_repository import UserAuthRepository
from app.schemas.user import TokenResponse

class UserAuthService:
    def __init__(self, db: Session):
        self.user_repo = UserAuthRepository(db)

    def refresh_access_token(self, refresh_token: str | None) -> TokenResponse:
        """리프레시 토큰을 검증하고 새로운 액세스 토큰을 발급합니다."""
        invalid_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="리프레시 토큰이 유효하지 않거나 만료되었습니다. 다시 로그인해주세요.",
        )

        if not refresh_token:
            raise invalid_exception

        try:
            # 토큰 디코딩 및 'refresh' 타입 검증
            user_id = decode_token(refresh_token, expected_type="refresh")
        except (jwt.PyJWTError, ValueError, KeyError):
            raise invalid_exception

        # DB에서 유저 조회
        user = self.user_repo.get_by_id(user_id)
        if user is None:
            raise invalid_exception

        # 비활성 계정 체크
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="비활성화된 사용자입니다."
            )

        # 새로운 액세스 토큰 반환 (리프레시 토큰은 재발급하지 않음)
        return TokenResponse(
            access_token=create_access_token(user.id),
            token_type="bearer",
            expires_in=1800,
        )