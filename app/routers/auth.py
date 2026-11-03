import jwt
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError

from fastapi import APIRouter, HTTPException, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.models.user import User
from app.schemas.user import (
    LoginRequest,
    SignupRequest,
    SignupResponse,
    TokenResponse,
)
from app.services import user_auth_service
# 로그인 쿠키 처리 추가
from app.core.security import (
    REFRESH_COOKIE_NAME,
    clear_refresh_cookie,
    create_access_token,
    create_refresh_token,
    decode_token,
    set_refresh_cookie,
)

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
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),  # Swagger Authorize·프론트 FormData 모두 form 형식
    db: AsyncSession = Depends(async_get_db),
):
    """
    이메일과 비밀번호를 검증하여 JWT Access Token 및 사용자 정보를 반환합니다.
    """
    # form의 username 칸에 이메일이 들어온다 → 기존 서비스가 쓰는 LoginRequest로 변환
    try:
        req = LoginRequest(email=form_data.username, password=form_data.password)
    except ValidationError:
        # 이메일 형식이 아니면 일반 로그인 실패와 같은 메시지로 응답
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 일치하지 않습니다.",
        )

    token_data = await user_auth_service.authenticate_user(db=db, req=req)
    refresh_token = create_refresh_token(token_data.user.id)
    set_refresh_cookie(response, refresh_token)
    return token_data


# [추가] POST / refresh (토큰 재발급, NFR-USER-001)
# 프론트(apis.js)는 Access Token 이 만료(401)되면 이 주소를 부른다.
# 이 엔드포인트가 없어서 405가 나고 → 프론트가 로그아웃 → 로그아웃도 401 → 다시 refresh ... 무한 반복되던 문제 해결
@router.post(
    "/refresh",
    summary="Access Token 재발급 (NFR-USER-001)",
)
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(async_get_db),
):
    """
    HTTP-only 쿠키의 refresh_token 을 검증해서 새 Access Token 을 발급합니다.
    - 쿠키가 없거나, 만료·위조됐거나, access 토큰을 넣은 경우 → 401
    - 탈퇴(비활성)했거나 없는 사용자 → 401
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="다시 로그인해 주세요.",
    )

    token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not token:
        raise credentials_exception

    try:
        user_id = decode_token(token, expected_type="refresh")
    except (jwt.PyJWTError, ValueError, KeyError):
        clear_refresh_cookie(response)
        raise credentials_exception

    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        clear_refresh_cookie(response)
        raise credentials_exception

    # refresh 토큰도 새로 바꿔 준다 (계속 사용하는 동안 7일 유효기간이 연장됨)
    set_refresh_cookie(response, create_refresh_token(user.id))
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}


# POST / logout (로그아웃)
@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="로그아웃",
)
async def logout(response: Response):
    """
    refresh_token 쿠키를 지워 세션을 종료합니다.
    [수정] Access Token 검사를 빼서, 토큰이 이미 만료된 상태에서도 로그아웃이 항상 성공하게 했습니다.
           (만료된 토큰으로 로그아웃을 누르면 401 → 프론트가 refresh 재시도 → 반복되는 문제 방지)
    """
    clear_refresh_cookie(response)
    return {"message": "성공적으로 로그아웃되었습니다."}