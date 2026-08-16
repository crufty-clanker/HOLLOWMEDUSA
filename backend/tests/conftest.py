import asyncio
import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from hollowmedusa.api.main import app
from hollowmedusa.storage.database import Base, get_db
from hollowmedusa.storage.models import (  # noqa: F401
    AgentModel,
    ContextModel,
    GraphModel,
    ModelModel,
    RunModel,
    UserModel,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def db_path():
    """Create a temp database file for the test session."""
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture(scope="session")
async def db_engine(db_path):
    """Create an async engine pointed at a temp SQLite file."""
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="session")
def client(db_engine):
    """Test client with overridden database dependency."""
    test_session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with test_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def db_session(db_engine):
    """Provide an async session for repository tests."""
    test_session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    session = test_session_factory()
    yield session
    # Don't close — engine is still in use
