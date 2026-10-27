from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User

class UserAuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        """유저 ID로 사용자를 조회합니다."""
        return self.db.get(User, user_id)