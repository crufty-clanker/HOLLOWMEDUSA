from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...storage.database import get_db
from ...storage.repositories.agent_repository import AgentRepository

router = APIRouter()


class AgentResponse(BaseModel):
    id: str
    config: dict


class AgentUpdate(BaseModel):
    system_prompt: str | None = None
    primary_model: str | None = None
    fallback_models: list[str] | None = None


@router.get("/", response_model=list[AgentResponse])
async def list_agents(db: AsyncSession = Depends(get_db)):
    repo = AgentRepository(db)
    agents = await repo.list_all()
    return [AgentResponse(id=a.id, config=a.config) for a in agents]


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, update: AgentUpdate, db: AsyncSession = Depends(get_db)):
    repo = AgentRepository(db)
    agent = await repo.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Merge updates
    config = agent.config.copy()
    if update.system_prompt is not None:
        config["system_prompt"] = update.system_prompt
    if update.primary_model is not None:
        config["primary_model"] = update.primary_model
    if update.fallback_models is not None:
        config["fallback_models"] = update.fallback_models

    await repo.update(agent_id, config)
    return AgentResponse(id=agent.id, config=config)
