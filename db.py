from contextlib import asynccontextmanager

from config import settings
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, create_async_engine

from fastapi import Depends

db_url = (
    f"postgresql+asyncpg://"
    f"{settings.DATABASE_USER}:"
    f"{settings.DATABASE_PASSWORD}@"
    f"{settings.DATABASE_HOST}:"
    f"{settings.DATABASE_PORT}/"
    f"{settings.DATABASE_DB}"
)

persistent_engine = create_async_engine(
    db_url,
    # encoding="utf-8",
    echo=settings.get("DATABASE_ECHO_MODE", False),
    max_overflow=settings.get("DB_CONN_MAX_OVERFLOW", 25),
    connect_args={"server_settings": {"application_name": settings.APPNAME}},
)


async def get_session() -> AsyncSession:
    async with AsyncSession(persistent_engine) as session, session.begin():
        yield session


get_session_dep: AsyncSession = Depends(get_session)
get_session = asynccontextmanager(get_session)


async def ro_session() -> AsyncConnection:
    async with persistent_engine.connect() as session:
        await session.execution_options(isolation_level="AUTOCOMMIT")
        yield session


ro_session_dep: AsyncConnection = Depends(ro_session)
ro_session = asynccontextmanager(ro_session)
