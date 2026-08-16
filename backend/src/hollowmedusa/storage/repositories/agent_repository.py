from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import AgentModel


class AgentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, agent_id: str, config: dict) -> AgentModel:
        agent = AgentModel(id=agent_id, config=config)
        self.db.add(agent)
        await self.db.commit()
        await self.db.refresh(agent)
        return agent

    async def get(self, agent_id: str) -> AgentModel | None:
        result = await self.db.execute(select(AgentModel).where(AgentModel.id == agent_id))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[AgentModel]:
        result = await self.db.execute(select(AgentModel))
        return list(result.scalars().all())

    async def update(self, agent_id: str, config: dict):
        agent = await self.get(agent_id)
        if agent:
            agent.config = config
            await self.db.commit()

    async def upsert(self, agent_id: str, config: dict):
        agent = await self.get(agent_id)
        if agent:
            agent.config = config
        else:
            agent = AgentModel(id=agent_id, config=config)
            self.db.add(agent)
        await self.db.commit()
