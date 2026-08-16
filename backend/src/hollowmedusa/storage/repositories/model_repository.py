from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ModelModel


class ModelRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, model_id: str, config: dict) -> ModelModel:
        model = ModelModel(id=model_id, config=config)
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return model

    async def get(self, model_id: str) -> ModelModel | None:
        result = await self.db.execute(select(ModelModel).where(ModelModel.id == model_id))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[ModelModel]:
        result = await self.db.execute(select(ModelModel))
        return list(result.scalars().all())

    async def update(self, model_id: str, config: dict):
        model = await self.get(model_id)
        if model:
            model.config = config
            await self.db.commit()

    async def upsert(self, model_id: str, config: dict):
        model = await self.get(model_id)
        if model:
            model.config = config
        else:
            model = ModelModel(id=model_id, config=config)
            self.db.add(model)
        await self.db.commit()
