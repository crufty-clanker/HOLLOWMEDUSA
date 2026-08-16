"""PostgreSQL async engine support."""
import os

from sqlalchemy.ext.asyncio import create_async_engine


def create_postgres_engine():
    """Create async PostgreSQL engine from environment."""
    url = os.getenv(
        "POSTGRES_URL",
        "postgresql+asyncpg://user:pass@localhost:5432/hollowmedusa",
    )
    return create_async_engine(url, echo=False)
