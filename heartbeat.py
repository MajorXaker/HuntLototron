import random

import sqlalchemy as sa
from config import settings
from db import get_session_dep
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter
from starlette.responses import JSONResponse, Response

heartbeat_router = APIRouter()


@heartbeat_router.get("/__version__", include_in_schema=False)
async def version():
    return JSONResponse(
        {
            "build": settings.PIPELINE_ID,
            "version": settings.VERSION,
            "source": settings.SOURCE,
            "commit": settings.GIT_COMMIT,
        }
    )


@heartbeat_router.get("/__heartbeat__", include_in_schema=False)
async def heartbeat(db: AsyncSession = get_session_dep):
    checks = {}
    is_500 = False

    try:
        if await db.execute(sa.text("SELECT 1")):
            checks["database"] = "ok"
        else:
            checks["database"] = "error"
            is_500 = True
    except BaseException:
        checks["database"] = "error"
        is_500 = True

    data = {
        "status": "ok" if not is_500 else "error",
        "random": random.randint(1, 1000),
        "checks": checks,
    }

    return JSONResponse(
        data,
        status_code=200 if not is_500 else 500,
    )


@heartbeat_router.get("/__lbheartbeat__", include_in_schema=False)
async def lbheartbeat():
    return Response(status_code=200)
