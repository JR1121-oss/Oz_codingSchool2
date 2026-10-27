from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# 프로젝트 내 파일 경로 확인 (예: app.core.database 또는 app.core.db.databases)
from app.core.database import get_db
from app.core.deps import get_current_user
# 프로젝트 내 보안 유틸 경로 확인 (비밀번호 검증/해싱)
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import PasswordChangeRequest, UserBase, UserProfileUpdate

router = APIRouter(prefix="/api/v1/users/me", tags=["Mypage"])


# 1. 마이페이지 조회 (REQ-USER-006)
@router.get("", response_model=UserBase)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


# 2. 회원 정보 수정 (REQ-USER-007: 부서, 휴대폰번호 Partial 수정)
@router.patch("")
def update_my_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.department is not None:
        current_user.department = payload.department
    if payload.phone_number is not None:
        current_user.phone_number = payload.phone_number

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {
        "message": "Profile updated successfully.",
        "data": UserBase.model_validate(current_user),
    }


# 3. 비밀번호 변경 (REQ-USER-008: 기존 비밀번호 검증 후 새 비밀번호 적용)
@router.patch("/password")
def change_password(
    payload: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 기존 비밀번호 일치 검증
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password does not match.",
        )

    # 새로운 비밀번호 해싱 후 업데이트
    current_user.hashed_password = get_password_hash(payload.new_password)
    db.add(current_user)
    db.commit()

    return {"message": "Password changed successfully."}


# 4. 회원 탈퇴 (REQ-USER-009: Database에서 관련 정보 즉시 삭제)
@router.delete("")
def delete_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 요구사항에 명시된 'DB 즉시 삭제' 처리
    db.delete(current_user)
    db.commit()

    return {"message": "Account successfully deleted."}from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# 프로젝트 내 파일 경로 확인 (예: app.core.database 또는 app.core.db.databases)
from app.core.database import get_db
from app.core.deps import get_current_user
# 프로젝트 내 보안 유틸 경로 확인 (비밀번호 검증/해싱)
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import PasswordChangeRequest, UserBase, UserProfileUpdate

router = APIRouter(prefix="/api/v1/users/me", tags=["Mypage"])


# 1. 마이페이지 조회 (REQ-USER-006)
@router.get("", response_model=UserBase)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


# 2. 회원 정보 수정 (REQ-USER-007: 부서, 휴대폰번호 Partial 수정)
@router.patch("")
def update_my_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.department is not None:
        current_user.department = payload.department
    if payload.phone_number is not None:
        current_user.phone_number = payload.phone_number

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {
        "message": "Profile updated successfully.",
        "data": UserBase.model_validate(current_user),
    }


# 3. 비밀번호 변경 (REQ-USER-008: 기존 비밀번호 검증 후 새 비밀번호 적용)
@router.patch("/password")
def change_password(
    payload: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 기존 비밀번호 일치 검증
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password does not match.",
        )

    # 새로운 비밀번호 해싱 후 업데이트
    current_user.hashed_password = get_password_hash(payload.new_password)
    db.add(current_user)
    db.commit()

    return {"message": "Password changed successfully."}


# 4. 회원 탈퇴 (REQ-USER-009: Database에서 관련 정보 즉시 삭제)
@router.delete("")
def delete_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 요구사항에 명시된 'DB 즉시 삭제' 처리
    db.delete(current_user)
    db.commit()

    return {"message": "Account successfully deleted."}