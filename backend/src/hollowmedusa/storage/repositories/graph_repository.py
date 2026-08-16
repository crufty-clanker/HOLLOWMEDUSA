from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import GraphModel


class GraphRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, graph_id: str = "default") -> GraphModel | None:
        result = await self.db.execute(select(GraphModel).where(GraphModel.id == graph_id))
        return result.scalar_one_or_none()

    async def upsert(self, graph_id: str, topology: dict):
        graph = await self.get(graph_id)
        if graph:
            graph.topology = topology
        else:
            graph = GraphModel(id=graph_id, topology=topology)
            self.db.add(graph)
        graph.updated_at = datetime.utcnow()
        await self.db.commit()
