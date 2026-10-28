from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import LoginUserData, UserUpdateReq
from app.services import user_me_service

router = APIRouter()

# app/schemas/user.py에 import 한 LoginUserData로 response_model을 통일
# LoginUserData는 비밀번호 정보가 없는 응답용 DTO
@router.get(
    "/me", response_model=LoginUserData, summary="현재 로그인된 사용자 정보 조회"
)
async def get_my_info(
    current_user: User = Depends(get_current_user),
):
    """로그인된 사용자 본인의 프로필 및 계정 상태 정보를 반환합니다."""
    return current_user

# LoginUserData을 수정 요청(Request Body)용으로 사용하면 유효성 검증이나 비밀번호 수정 처리가 불가능
# 응답 모델까지 UserUpdateReq로 설정 시, 수정 결과로 비밀번호 관련 정보가 클라이언트에 다시 노출될 위험 있음
@router.patch(
    "/me", response_model=LoginUserData, summary="현재 로그인된 사용자 정보 수정"
)
async def update_my_info(
    req: UserUpdateReq,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    """로그인된 사용자 본인의 프로필 정보(이름, 비밀번호 등)를 수정합니다."""
    updated_user = await user_me_service.update_user_profile(
        db=db, user_id=current_user.id, req=req
    )
    return updated_user
