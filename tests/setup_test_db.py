#!/usr/bin/env python3
import asyncio

import asyncpg
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine

from config import settings as s
from db import db_url
from models import db_models as m

psql_url = (
    f"postgresql://{s.DATABASE_USER}:{s.DATABASE_PASSWORD}@{s.DATABASE_HOST}:5432"
)


def check_test_db():
    if (
        s.DATABASE_HOST
        not in (
            "localhost",
            "127.0.0.1",
            "postgres",
            "192.168.100.17",
        )
        or "amazonaws" in s.DATABASE_HOST
    ):
        raise Exception("Use local database only!")


async def setup_db_for_tests():
    check_test_db()
    conn = await asyncpg.connect(psql_url)

    await conn.execute(f'drop database if exists "{s.DATABASE_DB}"')
    await conn.execute("commit")
    await conn.execute(f'create database "{s.DATABASE_DB}"')
    await conn.execute("commit")

    e = create_async_engine(db_url)
    async with e.begin() as conn:
        await conn.run_sync(m.Model.metadata.create_all)
        await conn.execute(sa.text("commit"))
    await e.dispose()
    print("FIN")


if __name__ == "__main__":
    asyncio.run(setup_db_for_tests())
