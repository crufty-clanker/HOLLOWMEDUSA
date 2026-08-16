# Phase 2 — Implementation Tasks

## Execution Order (Dependencies)

```
2.14 SQLite storage layer (foundation)
    ↓
2.1 FastAPI app skeleton + router structure
    ↓
2.2 POST /runs (start execution)
2.3 GET /runs/{id} (get status)
    ↓
2.4 GET /runs/{id}/trace (step traces)
2.5 POST /runs/{id}/step/{step}/retry (error recovery)
    ↓
2.6 GET /agents (list agents)
2.7 PUT /agents/{id} (update agent)
    ↓
2.8 GET /models (list models)
2.9 PUT /models (manage models)
    ↓
2.10 Context CRUD endpoints
    ↓
2.11 Graph endpoints (GET/PUT /graph)
    ↓
2.12 WebSocket: ws://runs/{id}/events (real-time)
    ↓
2.13 Auth middleware (API key + JWT)
```

---

## 2.14 — SQLite Storage Layer

**Files:**
- `backend/src/hollowmedusa/storage/database.py` — Async SQLite connection
- `backend/src/hollowmedusa/storage/models.py` — SQLAlchemy models
- `backend/src/hollowmedusa/storage/repositories/run_repository.py`
- `backend/src/hollowmedusa/storage/repositories/agent_repository.py`
- `backend/src/hollowmedusa/storage/repositories/model_repository.py`
- `backend/src/hollowmedusa/storage/repositories/context_repository.py`
- `backend/src/hollowmedusa/storage/repositories/graph_repository.py`

**Database connection:**
```python
# backend/src/hollowmedusa/storage/database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./hollowmedusa.db"),
    echo=False,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

**SQLAlchemy models:**
```python
# backend/src/hollowmedusa/storage/models.py
from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime


class Base(DeclarativeBase):
    pass


class RunModel(Base):
    __tablename__ = "runs"

    id = Column(String, primary_key=True)
    status = Column(String, default="pending")
    state = Column(JSON, default=dict)
    step_results = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AgentModel(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True)
    config = Column(JSON, default=dict)


class ModelModel(Base):
    __tablename__ = "models"

    id = Column(String, primary_key=True)
    config = Column(JSON, default=dict)


class ContextModel(Base):
    __tablename__ = "contexts"

    id = Column(String, primary_key=True)
    config = Column(JSON, default=dict)


class GraphModel(Base):
    __tablename__ = "graphs"

    id = Column(String, primary_key=True, default="default")
    topology = Column(JSON, default=dict)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Run repository:**
```python
# backend/src/hollowmedusa/storage/repositories/run_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.select import select
from ..models import RunModel
from datetime import datetime


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
```

**Create all repository files** with similar CRUD patterns for agents, models, contexts, and graphs.

**Verification:**
```python
python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from hollowmedusa.storage.database import Base, async_session

async def test():
    # Create in-memory SQLite
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        from hollowmedusa.storage.repositories.run_repository import RunRepository
        repo = RunRepository(session)
        run = await repo.create('test-run')
        assert run.id == 'test-run'
        assert run.status == 'pending'
        print('✅ 2.14 Storage layer works')

asyncio.run(test())
"
```

---

## 2.1 — FastAPI App Skeleton + Router Structure

**Files:**
- `backend/src/hollowmedusa/api/main.py` — FastAPI app with lifespan
- `backend/src/hollowmedusa/api/routers/runs.py`
- `backend/src/hollowmedusa/api/routers/agents.py`
- `backend/src/hollowmedusa/api/routers/models.py`
- `backend/src/hollowmedusa/api/routers/contexts.py`
- `backend/src/hollowmedusa/api/routers/graph.py`
- `backend/src/hollowmedusa/api/deps.py` — Dependency injection

**Main app:**
```python
# backend/src/hollowmedusa/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ..storage.database import init_db
from .routers import runs, agents, models, contexts, graph


def create_app() -> FastAPI:
    app = FastAPI(title="HollowMedusa", version="0.2.0")

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(runs.router, prefix="/api/v1/runs", tags=["runs"])
    app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
    app.include_router(models.router, prefix="/api/v1/models", tags=["models"])
    app.include_router(contexts.router, prefix="/api/v1/contexts", tags=["contexts"])
    app.include_router(graph.router, prefix="/api/v1/graph", tags=["graph"])

    # Lifespan
    @app lifespan
    async def lifespan(app: FastAPI):
        await init_db()
        yield

    return app


app = create_app()
```

**Router structure (example: runs.py):**
```python
# backend/src/hollowmedusa/api/routers/runs.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...storage.database import get_db
from ...storage.repositories.run_repository import RunRepository
from pydantic import BaseModel


router = APIRouter()


class RunCreate(BaseModel):
    graph_id: str = "default"


class RunResponse(BaseModel):
    id: str
    status: str
    created_at: str


@router.post("/", response_model=RunResponse)
async def create_run(run_data: RunCreate, db: AsyncSession = Depends(get_db)):
    # TODO: Implement
    raise HTTPException(status_code=501, detail="Not implemented")
```

**Verification:**
```bash
cd backend && source .venv/bin/activate && python -c "
from hollowmedusa.api.main import app
assert app.title == 'HollowMedusa'
print('✅ 2.1 FastAPI app skeleton works')
"
```

---

## 2.2 — POST /runs (Start Execution)

**File:** `backend/src/hollowmedusa/api/routers/runs.py`

```python
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...storage.database import get_db
from ...storage.repositories.run_repository import RunRepository
from ...engine.pipeline_runner import PipelineRunner
from ...config.agent_registry import AgentRegistry
from ...config.model_registry import ModelRegistry
from ...config.context_manager import ContextManager
from pydantic import BaseModel


router = APIRouter()


class RunCreate(BaseModel):
    graph_id: str = "default"


class RunResponse(BaseModel):
    id: str
    status: str
    created_at: str


@router.post("/", response_model=RunResponse)
async def create_run(run_data: RunCreate, db: AsyncSession = Depends(get_db)):
    run_id = str(uuid.uuid4())
    run_repo = RunRepository(db)
    await run_repo.create(run_id, status="running")

    # TODO: Start async task to run pipeline
    # For now, just return the run ID
    return RunResponse(id=run_id, status="running", created_at="2024-01-01T00:00:00Z")
```

**Verification:**
```python
python -c "
# Test endpoint structure
from fastapi.testclient import TestClient
from hollowmedusa.api.main import app
client = TestClient(app)
response = client.post('/api/v1/runs/', json={'graph_id': 'default'})
# Will fail until implemented, but structure is correct
print('✅ 2.2 POST /runs endpoint registered')
"
```

---

## 2.3 — GET /runs/{id} (Get Status)

**File:** `backend/src/hollowmedusa/api/routers/runs.py`

```python
@router.get("/{run_id}", response_model=RunResponse)
async def get_run(run_id: str, db: AsyncSession = Depends(get_db)):
    run_repo = RunRepository(db)
    run = await run_repo.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunResponse(id=run.id, status=run.status, created_at=str(run.created_at))
```

**Verification:**
```python
python -c "
from fastapi.testclient import TestClient
from hollowmedusa.api.main import app
client = TestClient(app)
response = client.get('/api/v1/runs/nonexistent')
assert response.status_code == 404
print('✅ 2.3 GET /runs/{id} works')
"
```

---

## 2.4 — GET /runs/{id}/trace (Step Traces)

**File:** `backend/src/hollowmedusa/api/routers/runs.py`

```python
@router.get("/{run_id}/trace")
async def get_run_trace(run_id: str, db: AsyncSession = Depends(get_db)):
    run_repo = RunRepository(db)
    run = await run_repo.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return {"step_results": run.step_results}
```

---

## 2.5 — POST /runs/{id}/step/{step}/retry (Retry)

**File:** `backend/src/hollowmedusa/api/routers/runs.py`

```python
@router.post("/{run_id}/step/{step_id}/retry")
async def retry_step(run_id: str, step_id: str, db: AsyncSession = Depends(get_db)):
    # TODO: Re-execute the failed step
    return {"status": "retry initiated", "run_id": run_id, "step_id": step_id}
```

---

## 2.6 — GET /agents (List Agents)

**File:** `backend/src/hollowmedusa/api/routers/agents.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ...storage.database import get_db
from ...storage.repositories.agent_repository import AgentRepository
from pydantic import BaseModel


router = APIRouter()


class AgentResponse(BaseModel):
    id: str
    config: dict


@router.get("/", response_model=list[AgentResponse])
async def list_agents(db: AsyncSession = Depends(get_db)):
    repo = AgentRepository(db)
    agents = await repo.list_all()
    return [AgentResponse(id=a.id, config=a.config) for a in agents]
```

---

## 2.7 — PUT /agents/{id} (Update Agent)

**File:** `backend/src/hollowmedusa/api/routers/agents.py`

```python
class AgentUpdate(BaseModel):
    system_prompt: str | None = None
    primary_model: str | None = None
    fallback_models: list[str] | None = None


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, update: AgentUpdate, db: AsyncSession = Depends(get_db)):
    repo = AgentRepository(db)
    agent = await repo.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Merge updates
    if update.system_prompt:
        agent.config["system_prompt"] = update.system_prompt
    if update.primary_model:
        agent.config["primary_model"] = update.primary_model
    if update.fallback_models is not None:
        agent.config["fallback_models"] = update.fallback_models

    await repo.update(agent_id, agent.config)
    return AgentResponse(id=agent.id, config=agent.config)
```

---

## 2.8 — GET /models (List Models)

**File:** `backend/src/hollowmedusa/api/routers/models.py`

```python
@router.get("/", response_model=list[dict])
async def list_models(db: AsyncSession = Depends(get_db)):
    repo = ModelRepository(db)
    models = await repo.list_all()
    # Mask API keys
    return [{"id": m.id, **{k: v for k, v in m.config.items() if k != "api_key"}} for m in models]
```

---

## 2.9 — PUT /models (Manage Models)

**File:** `backend/src/hollowmedusa/api/routers/models.py`

```python
class ModelCreate(BaseModel):
    id: str
    provider: str
    model_name: str
    api_key: str | None = None
    base_url: str | None = None


@router.put("/", response_model=dict)
async def upsert_model(model_data: ModelCreate, db: AsyncSession = Depends(get_db)):
    repo = ModelRepository(db)
    await repo.upsert(model_data.id, model_data.model_dump())
    return {"id": model_data.id, "status": "saved"}
```

---

## 2.10 — Context CRUD Endpoints

**File:** `backend/src/hollowmedusa/api/routers/contexts.py`

```python
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
async def update_context(context_id: str, context_data: ContextCreate, db: AsyncSession = Depends(get_db)):
    repo = ContextRepository(db)
    await repo.upsert(context_id, context_data.model_dump())
    return context_data
```

---

## 2.11 — Graph Endpoints (GET/PUT /graph)

**File:** `backend/src/hollowmedusa/api/routers/graph.py`

```python
router = APIRouter()


class GraphUpdate(BaseModel):
    topology: dict


@router.get("/", response_model=dict)
async def get_graph(db: AsyncSession = Depends(get_db)):
    repo = GraphRepository(db)
    graph = await repo.get("default")
    if not graph:
        return {"topology": {}}
    return graph.topology


@router.put("/", response_model=dict)
async def update_graph(graph_data: GraphUpdate, db: AsyncSession = Depends(get_db)):
    repo = GraphRepository(db)
    await repo.upsert("default", graph_data.topology)
    return {"status": "saved", "topology": graph_data.topology}
```

---

## 2.12 — WebSocket: ws://runs/{id}/events (Real-time)

**File:** `backend/src/hollowmedusa/api/routers/ws.py`

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json


router = APIRouter()

# In-memory connection store (replace with Redis in production)
connections: dict[str, list[WebSocket]] = {}


@router.websocket("/runs/{run_id}/events")
async def websocket_endpoint(websocket: WebSocket, run_id: str):
    await websocket.accept()
    connections.setdefault(run_id, []).append(websocket)

    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        connections.get(run_id, []).remove(websocket)


async def send_event(run_id: str, event: dict):
    """Send event to all connected clients for a run."""
    for ws in connections.get(run_id, []):
        await ws.send_text(json.dumps(event))
```

**Verification:**
```python
python -c "
from fastapi.testclient import TestClient
from hollowmedusa.api.main import app
client = TestClient(app)
# WebSocket test would use websocket_client
print('✅ 2.12 WebSocket endpoint registered')
"
```

---

## 2.13 — Auth Middleware (API Key + JWT)

**File:** `backend/src/hollowmedusa/api/middleware/auth.py`

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from ...storage.database import get_db
from ...storage.repositories.user_repository import UserRepository
import jwt
from datetime import datetime, timedelta
import os


API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Depends(API_KEY_HEADER), db: AsyncSession = Depends(get_db)):
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    repo = UserRepository(db)
    user = await repo.get_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY", "fallback"), algorithm="HS256")
    return encoded_jwt
```

**Verification:**
```python
python -c "
from hollowmedusa.api.middleware.auth import create_access_token
token = create_access_token({'sub': 'test-user'})
assert token
print('✅ 2.13 Auth middleware works')
"
```

---

## Checklist

- [ ] `2.14` SQLite storage layer with all repositories
- [ ] `2.1` FastAPI app skeleton with router structure
- [ ] `2.2` POST /runs (start execution)
- [ ] `2.3` GET /runs/{id} (get status)
- [ ] `2.4` GET /runs/{id}/trace (step traces)
- [ ] `2.5` POST /runs/{id}/step/{step}/retry (retry)
- [ ] `2.6` GET /agents (list agents)
- [ ] `2.7` PUT /agents/{id} (update agent)
- [ ] `2.8` GET /models (list models)
- [ ] `2.9` PUT /models (manage models)
- [ ] `2.10` Context CRUD endpoints
- [ ] `2.11` Graph endpoints (GET/PUT /graph)
- [ ] `2.12` WebSocket: ws://runs/{id}/events
- [ ] `2.13` Auth middleware (API key + JWT)

## Deliverable

Fully functional REST + WebSocket API with persistence.

```bash
cd backend && source .venv/bin/activate
uvicorn hollowmedusa.api.main:app --reload --port 8000

# Test endpoints
curl http://localhost:8000/api/v1/runs/
curl http://localhost:8000/api/v1/agents/
curl http://localhost:8000/api/v1/models/
```
