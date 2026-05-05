from typing import Any, AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from config import settings as st
from db import get_session_dep
from main import app
from models import db_models as m
from tests.creator import Creator

db_url = (
    "postgresql+asyncpg://"
    f"{st.DATABASE_USER}:"
    f"{st.DATABASE_PASSWORD}@"
    f"{st.DATABASE_HOST}:"
    f"{st.DATABASE_PORT}/"
    f"{st.DATABASE_DB}"
)


def check_test_db():
    if (
        st.DATABASE_HOST not in ("localhost", "127.0.0.1", "postgres")
        or "amazonaws" in st.DATABASE_HOST
    ):
        print(db_url)
        raise Exception("Use local database only!")


async def drop_everything(engine: Engine | AsyncEngine):
    async with engine.begin() as con:
        await con.run_sync(m.Model.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def engine():
    check_test_db()
    print(db_url)
    e = create_async_engine(db_url, echo=False, max_overflow=25)
    try:
        async with e.begin() as con:
            await con.run_sync(m.Model.metadata.create_all)

        yield e
    finally:
        await drop_everything(e)
        await e.dispose()


@pytest_asyncio.fixture(scope="function")
async def dbsession(engine) -> AsyncGenerator[AsyncSession, Any]:
    async with AsyncSession(bind=engine) as session:
        yield session


@pytest_asyncio.fixture
async def test_client_rest(dbsession: AsyncSession) -> AsyncClient:
    def override_get_db():
        test_db = dbsession
        yield test_db

    app.dependency_overrides[get_session_dep.dependency] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
def creator(dbsession) -> Creator:
    return Creator(dbsession)
