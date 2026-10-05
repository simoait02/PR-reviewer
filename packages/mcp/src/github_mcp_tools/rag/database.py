import os
from functools import lru_cache

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

DEFAULT_DB_HOST = "localhost"
DEFAULT_DB_PORT = "5432"
EMBEDDING_MODEL = "text-embedding-3-small"


def get_database_url() -> URL:
    """Build the shared database URL used by ingestion and retrieval."""
    return URL.create(
        drivername="postgresql+psycopg",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.getenv("DB_HOST", DEFAULT_DB_HOST),
        port=os.getenv("DB_PORT", DEFAULT_DB_PORT),
        database=os.environ["DB_NAME"],
    )


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    """Return the process-wide async engine for the RAG database."""
    return create_async_engine(
        get_database_url(),
        pool_size=5,
        max_overflow=2,
        pool_timeout=30,
        pool_pre_ping=True,
    )


@lru_cache(maxsize=1)
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the process-wide session factory backed by the shared database."""
    return async_sessionmaker(
        get_engine(),
        expire_on_commit=False,
    )
