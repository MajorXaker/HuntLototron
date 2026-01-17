import sqlalchemy as sa
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session_dep
from logic.analytics.teammate_stats import (
    get_separate_teammates_stats,
    get_teammate_composition_stats,
)
from models import db_models as m
from models.schemas.analytics import TeammateAnalytics

analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])


@analytics_router.get("/teammates", response_model=TeammateAnalytics)
async def get_teammate_analytics(db: AsyncSession = get_session_dep):
    matches_total = await db.scalar(sa.select(sa.func.count(m.Match.id)))

    teammate_stats = await get_separate_teammates_stats(db, matches_total)
    team_composition_stats = await get_teammate_composition_stats(db, matches_total)

    return TeammateAnalytics(
        by_teammates=teammate_stats,
        by_team_compositions=team_composition_stats,
        matches_total=matches_total,
    )
