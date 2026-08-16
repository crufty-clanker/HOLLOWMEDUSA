from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..storage.database import init_db
from .routers import agents, contexts, graph, models, runs, ws


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


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
    app.include_router(ws.router, tags=["websocket"])

    # Health check
    @app.get("/health")
    async def health():
        return {"status": "ok", "version": "0.2.0"}

    return app


app = create_app()
