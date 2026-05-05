from typing import Literal

import sqlalchemy as sa
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from db import get_session_dep
from logic.analytics.map_stats import get_map_stats
from logic.analytics.teammate_stats import (
    get_separate_teammates_stats,
    get_teammate_composition_stats,
)
from logic.analytics.weapon_stats import get_weapon_stats
from models import db_models as m
from models.enums.gamemode import GameModeEnum
from models.schemas.analytics import (
    MapAnalytics,
    TeammateAnalytics,
    WeaponAnalytics,
)

analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _validate_game_mode(game_mode: str):
    if game_mode not in GameModeEnum:
        return None
    return GameModeEnum(game_mode)


async def _matches_total_for_mode(db: AsyncSession, game_mode: GameModeEnum) -> int:
    return await db.scalar(
        sa.select(sa.func.count(m.Match.id)).where(
            m.Match.game_mode == game_mode,
            m.Match.wl_status.isnot(None),
        )
    )


@analytics_router.get("/teammates", response_model=TeammateAnalytics)
async def get_teammate_analytics(
    db: AsyncSession = get_session_dep,
    game_mode: Literal["hunt", "clash", "quickplay"] = GameModeEnum.HUNT,
):
    mode = _validate_game_mode(game_mode)
    if mode is None:
        return JSONResponse(status_code=400, content={"detail": "Invalid game_mode"})

    matches_total = await db.scalar(
        sa.select(sa.func.count(m.Match.id)).where(m.Match.game_mode == mode)
    )

    teammate_stats = await get_separate_teammates_stats(
        session=db,
        matches_total=matches_total,
        game_mode=mode,
    )
    team_composition_stats = await get_teammate_composition_stats(
        session=db,
        matches_total=matches_total,
        game_mode=mode,
    )

    return TeammateAnalytics(
        by_teammates=teammate_stats,
        by_team_compositions=team_composition_stats,
        matches_total=matches_total,
    )


@analytics_router.get("/weapons", response_model=WeaponAnalytics)
async def get_weapon_analytics(
    db: AsyncSession = get_session_dep,
    game_mode: Literal["hunt", "clash", "quickplay"] = GameModeEnum.HUNT,
):
    mode = _validate_game_mode(game_mode)
    if mode is None:
        return JSONResponse(status_code=400, content={"detail": "Invalid game_mode"})

    matches_total = await _matches_total_for_mode(db, mode)

    weapon_stats = await get_weapon_stats(
        session=db,
        matches_total=matches_total,
        game_mode=mode,
    )

    return WeaponAnalytics(by_weapons=weapon_stats, matches_total=matches_total)


@analytics_router.get("/maps", response_model=MapAnalytics)
async def get_map_analytics(
    db: AsyncSession = get_session_dep,
    game_mode: Literal["hunt", "clash", "quickplay"] = GameModeEnum.HUNT,
):
    mode = _validate_game_mode(game_mode)
    if mode is None:
        return JSONResponse(status_code=400, content={"detail": "Invalid game_mode"})

    matches_total = await _matches_total_for_mode(db, mode)

    map_stats = await get_map_stats(
        session=db,
        matches_total=matches_total,
        game_mode=mode,
    )

    return MapAnalytics(by_maps=map_stats, matches_total=matches_total)
