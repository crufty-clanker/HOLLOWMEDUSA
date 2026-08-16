from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import RunModel


class RunRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, run_id: str, status: str = "pending") -> RunModel:
        run = RunModel(id=run_id, status=status, state={}, step_results=[])
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        return run

    async def get(self, run_id: str) -> RunModel | None:
        result = await self.db.execute(select(RunModel).where(RunModel.id == run_id))
        return result.scalar_one_or_none()

    async def update_status(self, run_id: str, status: str):
        run = await self.get(run_id)
        if run:
            run.status = status
            run.updated_at = datetime.utcnow()
            await self.db.commit()

    async def update_state(self, run_id: str, state: dict):
        run = await self.get(run_id)
        if run:
            run.state = state
            run.updated_at = datetime.utcnow()
            await self.db.commit()

    async def update_step_results(self, run_id: str, step_results: list):
        run = await self.get(run_id)
        if run:
            run.step_results = step_results
            run.updated_at = datetime.utcnow()
            await self.db.commit()
