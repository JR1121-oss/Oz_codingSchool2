from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
# 프로젝트 보안 유틸 함수 임포트 (경로가 다를 경우 맞춰서 조정해주세요)
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import PasswordChangeRequest, UserBase, UserProfileUpdate

router = APIRouter(prefix="/api/v1/users/me", tags=["Mypage"])


# D 파트: 내 프로필 조회 (REQ-USER-006)
@router.get("", response_model=UserBase)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


# D 파트: 프로필 수정 (부서, 전화번호) (REQ-USER-007)
@router.patch("")
def update_my_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 전달된 값만 부분 업데이트
    if payload.department is not None:
        current_user.department = payload.department
    if payload.phone_number is not None:
        current_user.phone_number = payload.phone_number

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {
        "message": "Profile updated successfully.",
        "data": current_user,
    }


# D 파트: 비밀번호 변경 (REQ-USER-008)
@router.patch("/password")
def change_password(
    payload: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. 현재 비밀번호 검증
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password does not match.",
        )

    # 2. 신규 비밀번호 해싱 후 업데이트
    current_user.hashed_password = get_password_hash(payload.new_password)
    db.add(current_user)
    db.commit()

    return {"message": "Password changed successfully."}


# D 파트: 회원 탈퇴 (REQ-USER-009)
@router.delete("")
def delete_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 소프트 삭제(Soft Delete: 비활성화) 처리
    current_user.is_active = False
    db.add(current_user)
    
    # 만약 DB에서 완전히 영구 삭제(Hard Delete)를 요구한다면 아래 주석을 해제하고 위 두 줄을 지우면 됩니다.
    # db.delete(current_user)

    db.commit()

    return {"message": "Account successfully deleted."}