from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...storage.database import get_db
from ...storage.repositories.graph_repository import GraphRepository

router = APIRouter()


class GraphUpdate(BaseModel):
    topology: dict


class GraphResponse(BaseModel):
    topology: dict


@router.get("/", response_model=GraphResponse)
async def get_graph(db: AsyncSession = Depends(get_db)):
    repo = GraphRepository(db)
    graph = await repo.get("default")
    if not graph:
        return GraphResponse(topology={})
    return GraphResponse(topology=graph.topology)


@router.put("/", response_model=GraphResponse)
async def update_graph(graph_data: GraphUpdate, db: AsyncSession = Depends(get_db)):
    repo = GraphRepository(db)
    await repo.upsert("default", graph_data.topology)
    return GraphResponse(topology=graph_data.topology)
