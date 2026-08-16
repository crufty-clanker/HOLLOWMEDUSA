import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...storage.database import get_db
from ...storage.repositories.run_repository import RunRepository

router = APIRouter()


class RunCreate(BaseModel):
    graph_id: str = "default"


class RunResponse(BaseModel):
    id: str
    status: str
    created_at: datetime


class RunTraceResponse(BaseModel):
    step_results: list


@router.post("/", response_model=RunResponse)
async def create_run(run_data: RunCreate, db: AsyncSession = Depends(get_db)):
    run_id = str(uuid.uuid4())
    run_repo = RunRepository(db)
    run = await run_repo.create(run_id, status="running")
    return RunResponse(id=run.id, status=run.status, created_at=run.created_at)


@router.get("/{run_id}", response_model=RunResponse)
async def get_run(run_id: str, db: AsyncSession = Depends(get_db)):
    run_repo = RunRepository(db)
    run = await run_repo.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunResponse(id=run.id, status=run.status, created_at=run.created_at)


@router.get("/{run_id}/trace", response_model=RunTraceResponse)
async def get_run_trace(run_id: str, db: AsyncSession = Depends(get_db)):
    run_repo = RunRepository(db)
    run = await run_repo.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunTraceResponse(step_results=run.step_results or [])


@router.post("/{run_id}/step/{step_id}/retry")
async def retry_step(run_id: str, step_id: str, db: AsyncSession = Depends(get_db)):
    run_repo = RunRepository(db)
    run = await run_repo.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    # TODO: Re-execute the failed step
    return {"status": "retry initiated", "run_id": run_id, "step_id": step_id}
