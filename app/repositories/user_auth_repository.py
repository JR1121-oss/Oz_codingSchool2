from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserAuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """유저 ID로 사용자를 조회합니다."""
        return await self.db.get(User, user_id)