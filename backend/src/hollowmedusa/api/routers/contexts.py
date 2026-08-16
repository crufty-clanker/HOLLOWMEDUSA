from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...storage.database import get_db
from ...storage.repositories.context_repository import ContextRepository

router = APIRouter()


class ContextCreate(BaseModel):
    id: str
    name: str
    description: str = ""
    files: list[str] = []
    steps: list[str] = []


class ContextResponse(BaseModel):
    id: str
    name: str
    description: str
    files: list[str]
    steps: list[str]


@router.get("/", response_model=list[ContextResponse])
async def list_contexts(db: AsyncSession = Depends(get_db)):
    repo = ContextRepository(db)
    contexts = await repo.list_all()
    return [ContextResponse(**c.config) for c in contexts]


@router.post("/", response_model=ContextResponse)
async def create_context(context_data: ContextCreate, db: AsyncSession = Depends(get_db)):
    repo = ContextRepository(db)
    await repo.create(context_data.id, context_data.model_dump())
    return context_data


@router.put("/{context_id}", response_model=ContextResponse)
async def update_context(
    context_id: str,
    context_data: ContextCreate,
    db: AsyncSession = Depends(get_db),
):
    repo = ContextRepository(db)
    await repo.upsert(context_id, context_data.model_dump())
    return context_data
