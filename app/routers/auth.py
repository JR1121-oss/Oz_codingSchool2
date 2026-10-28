from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import (
    LoginRequest,
    SignupRequest,
    SignupResponse,
    TokenResponse,
)
from app.services import user_auth_service
# 로그인 쿠키 처리 추가
from app.core.security import set_refresh_cookie, clear_refresh_cookie, create_refresh_token

router = APIRouter()

# POST / signup (회원가입)
@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="신규 회원가입 (REQ-USER-001)",
)
async def signup(
    req: SignupRequest,
    db: AsyncSession = Depends(async_get_db),
):
    """
    이메일, 비밀번호, 이름, 부서, 성별, 전화번호를 입력받아 신규 회원을 등록합니다.
    """
    new_user = await user_auth_service.register_user(db=db, req=req)
    return SignupResponse(
        message="회원가입이 완료되었습니다.",
        user=new_user,
    )

# POST / login (로그인)
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="로그인 및 토큰 발급 (REQ-USER-002)",
)
async def login(
    req: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(async_get_db),
):
    """
    이메일과 비밀번호를 검증하여 JWT Access Token 및 사용자 정보를 반환합니다.
    """
    token_data = await user_auth_service.authenticate_user(db=db, req=req)
    # 서비스가 refresh 토큰을 이미 만들어 반환한다면 그 값을 사용
    refresh_token = create_refresh_token(token_data.user.id)
    set_refresh_cookie(response, refresh_token)
    return token_data

# POST / logout (로그아웃)
@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="로그아웃",
)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
):
    """
    현재 로그인된 사용자의 섹션을 종료합니다. (클라이언트 측 토큰 폐기 안내)
    """
    clear_refresh_cookie(response)
    return {"message": "성공적으로 로그아웃되었습니다."}
