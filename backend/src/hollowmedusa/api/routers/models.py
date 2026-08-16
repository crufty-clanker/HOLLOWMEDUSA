from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...storage.database import get_db
from ...storage.repositories.model_repository import ModelRepository

router = APIRouter()


class ModelCreate(BaseModel):
    id: str
    provider: str
    model_name: str
    api_key: str | None = None
    base_url: str | None = None


class ModelResponse(BaseModel):
    id: str
    provider: str
    model_name: str
    base_url: str | None


@router.get("/", response_model=list[ModelResponse])
async def list_models(db: AsyncSession = Depends(get_db)):
    repo = ModelRepository(db)
    models = await repo.list_all()
    # Mask API keys
    return [
        ModelResponse(
            id=m.id,
            provider=m.config.get("provider", ""),
            model_name=m.config.get("model_name", ""),
            base_url=m.config.get("base_url"),
        )
        for m in models
    ]


@router.put("/", response_model=dict)
async def upsert_model(model_data: ModelCreate, db: AsyncSession = Depends(get_db)):
    repo = ModelRepository(db)
    await repo.upsert(model_data.id, model_data.model_dump())
    return {"id": model_data.id, "status": "saved"}
