import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from models import db_models as m
from models.dto.teammate_stats import MapStats
from models.enums.gamemode import GameModeEnum


async def get_map_stats(
    session: AsyncSession,
    matches_total: int,
    game_mode: GameModeEnum = GameModeEnum.HUNT,
) -> list[MapStats]:
    """Aggregate stats per map. K/D/A are summed across all match_player_data
    entries (team totals) for matches on each map.
    """

    mpd = m.MatchPlayerData.__table__.alias("mpd")

    match_kda = (
        sa.select(
            m.Match.id.label("match_id"),
            m.Match.map_id,
            m.Match.wl_status,
            m.Match.date,
            m.Match.playtime,
            (
                sa.func.coalesce(
                    sa.select(sa.func.sum(mpd.c.kills))
                    .where(
                        mpd.c.id.in_(
                            [
                                m.Match.player_1_match_data_id,
                                m.Match.player_2_match_data_id,
                                m.Match.player_3_match_data_id,
                            ]
                        )
                    )
                    .scalar_subquery(),
                    0,
                )
            ).label("kills"),
            (
                sa.func.coalesce(
                    sa.select(sa.func.sum(mpd.c.deaths))
                    .where(
                        mpd.c.id.in_(
                            [
                                m.Match.player_1_match_data_id,
                                m.Match.player_2_match_data_id,
                                m.Match.player_3_match_data_id,
                            ]
                        )
                    )
                    .scalar_subquery(),
                    0,
                )
            ).label("deaths"),
            (
                sa.func.coalesce(
                    sa.select(sa.func.sum(mpd.c.assists))
                    .where(
                        mpd.c.id.in_(
                            [
                                m.Match.player_1_match_data_id,
                                m.Match.player_2_match_data_id,
                                m.Match.player_3_match_data_id,
                            ]
                        )
                    )
                    .scalar_subquery(),
                    0,
                )
            ).label("assists"),
        )
        .where(
            m.Match.wl_status.isnot(None),
            m.Match.game_mode == game_mode,
        )
        .subquery("match_kda")
    )

    map_t = m.Map.__table__.alias("map_t")

    query = (
        sa.select(
            match_kda.c.map_id,
            map_t.c.name.label("map_name"),
            sa.func.count().label("total_matches"),
            sa.func.count().filter(match_kda.c.wl_status == "win").label("win"),
            sa.func.count().filter(match_kda.c.wl_status == "lose").label("lose"),
            sa.func.count().filter(match_kda.c.wl_status == "flee").label("flee"),
            sa.func.round(
                sa.cast(
                    sa.func.count().filter(match_kda.c.wl_status == "win"),
                    sa.Numeric,
                )
                / sa.func.nullif(sa.func.count(), 0)
                * 100,
                3,
            ).label("win_ratio_percent"),
            sa.func.min(match_kda.c.date).label("first_match_date"),
            sa.func.max(match_kda.c.date).label("last_match_date"),
            sa.func.percentile_cont(0.5)
            .within_group(match_kda.c.playtime)
            .label("median_playtime"),
            sa.func.coalesce(sa.func.sum(match_kda.c.kills), 0).label("kills_sum"),
            sa.func.coalesce(sa.func.sum(match_kda.c.deaths), 0).label("deaths_sum"),
            sa.func.coalesce(sa.func.sum(match_kda.c.assists), 0).label("assists_sum"),
        )
        .select_from(match_kda.outerjoin(map_t, match_kda.c.map_id == map_t.c.id))
        .group_by(match_kda.c.map_id, map_t.c.name)
        .order_by(match_kda.c.map_id.nulls_last())
    )

    rows = (await session.execute(query)).fetchall()

    return [
        MapStats(
            map_id=row.map_id,
            map_name=row.map_name,
            wins=row.win,
            losses=row.lose,
            flees=row.flee,
            match_share=(row.total_matches / matches_total) * 100
            if matches_total
            else 0.0,
            total_matches=row.total_matches,
            winrate=row.win_ratio_percent or 0.0,
            first_match=row.first_match_date,
            last_match=row.last_match_date,
            median_playtime_seconds=(
                row.median_playtime.seconds if row.median_playtime else 0.0
            ),
            kills=row.kills_sum,
            deaths=row.deaths_sum,
            assists=row.assists_sum,
        )
        for row in rows
    ]
