import jwt
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.deps import get_current_user
from app.core.security import clear_refresh_cookie, create_access_token, decode_token
from app.models.user import User
from app.schemas.user import TokenResponse

router = APIRouter(prefix="/api/v1/users", tags=["Auth"])


# B 파트: 액세스 토큰 재발급
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str | None = Cookie(None),
    db: AsyncSession = Depends(async_get_db),
):
    invalid = HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "리프레시 토큰이 유효하지 않거나 만료되었습니다. 다시 로그인해주세요.",
    )

    # 쿠키 없음
    if not refresh_token:
        raise invalid

    # 위조 / 만료 / 액세스 토큰을 쿠키에 넣은 경우
    try:
        user_id = decode_token(refresh_token, expected_type="refresh")
    except (jwt.PyJWTError, ValueError, KeyError):
        raise invalid

    # 토큰의 user_id에 해당하는 유저가 없음
    user = await db.get(User, user_id)
    if user is None:
        raise invalid

    # 비활성 계정
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "비활성화된 사용자입니다.")

    # 리프레시 토큰은 새로 발급하지 않는다 (7일 후 재로그인)
    return TokenResponse(
        access_token=create_access_token(user.id),
        token_type="bearer",
        expires_in=1800,
    )


# B 파트: 로그아웃
@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
):
    # Max-Age=0 으로 refresh_token 쿠키 만료
    # (로그인에서 set_cookie 한 속성과 일치해야 정상적으로 삭제됩니다)
    clear_refresh_cookie(response)
    # 반환값 없음: 204 응답이 나가고, 위에서 설정한 Set-Cookie 헤더가 그대로 유지됩니다.