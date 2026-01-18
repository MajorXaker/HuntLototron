from typing import Literal

import sqlalchemy as sa
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from db import get_session_dep
from logic.analytics.teammate_stats import (
    get_separate_teammates_stats,
    get_teammate_composition_stats,
)
from models import db_models as m
from models.enums.gamemode import GameModeEnum
from models.schemas.analytics import TeammateAnalytics

analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])


@analytics_router.get("/teammates", response_model=TeammateAnalytics)
async def get_teammate_analytics(
    db: AsyncSession = get_session_dep,
    game_mode: Literal["hunt", "clash", "quickplay"] = GameModeEnum.HUNT,
):
    if game_mode not in GameModeEnum:
        return JSONResponse(status_code=400, content={"detail": "Invalid game_mode"})

    game_mode = GameModeEnum(game_mode)

    matches_total = await db.scalar(
        sa.select(sa.func.count(m.Match.id)).where(m.Match.game_mode == game_mode)
    )

    teammate_stats = await get_separate_teammates_stats(
        session=db,
        matches_total=matches_total,
        game_mode=game_mode,
    )
    team_composition_stats = await get_teammate_composition_stats(
        session=db,
        matches_total=matches_total,
        game_mode=game_mode,
    )

    return TeammateAnalytics(
        by_teammates=teammate_stats,
        by_team_compositions=team_composition_stats,
        matches_total=matches_total,
    )
