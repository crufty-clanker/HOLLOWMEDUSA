from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import UserModel


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: str,
        username: str,
        api_key: str,
        hashed_password: str,
    ) -> UserModel:
        user = UserModel(
            id=user_id,
            username=username,
            api_key=api_key,
            hashed_password=hashed_password,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get(self, user_id: str) -> UserModel | None:
        result = await self.db.execute(select(UserModel).where(UserModel.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_api_key(self, api_key: str) -> UserModel | None:
        result = await self.db.execute(select(UserModel).where(UserModel.api_key == api_key))
        return result.scalar_one_or_none()
