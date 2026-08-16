from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ContextModel


class ContextRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, context_id: str, config: dict) -> ContextModel:
        context = ContextModel(id=context_id, config=config)
        self.db.add(context)
        await self.db.commit()
        await self.db.refresh(context)
        return context

    async def get(self, context_id: str) -> ContextModel | None:
        result = await self.db.execute(select(ContextModel).where(ContextModel.id == context_id))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[ContextModel]:
        result = await self.db.execute(select(ContextModel))
        return list(result.scalars().all())

    async def update(self, context_id: str, config: dict):
        context = await self.get(context_id)
        if context:
            context.config = config
            await self.db.commit()

    async def upsert(self, context_id: str, config: dict):
        context = await self.get(context_id)
        if context:
            context.config = config
        else:
            context = ContextModel(id=context_id, config=config)
            self.db.add(context)
        await self.db.commit()
