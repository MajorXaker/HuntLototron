import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from models import db_models as m
from models.dto.teammate_stats import WeaponStats
from models.enums.gamemode import GameModeEnum


async def get_weapon_stats(
    session: AsyncSession,
    matches_total: int,
    game_mode: GameModeEnum = GameModeEnum.HUNT,
) -> list[WeaponStats]:
    """Aggregate stats per weapon: a match counts for a weapon if the weapon was
    present in any player's slot_a or slot_b for that match. K/D/A are summed
    across all match_player_data entries in those matches (team-level totals).
    """

    mpd = m.MatchPlayerData.__table__.alias("mpd")

    # Per-match aggregated K/D/A (sum across all 3 players) and match info
    match_kda = (
        sa.select(
            m.Match.id.label("match_id"),
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

    # match_id -> weapon_id presence (DISTINCT to count a match once per weapon)
    mpd1 = m.MatchPlayerData.__table__.alias("mpd1")
    weapon_presence = (
        sa.select(
            m.Match.id.label("match_id"),
            mpd1.c.slot_a_weapon_id.label("weapon_id"),
        )
        .select_from(
            m.Match.__table__.join(
                mpd1,
                mpd1.c.id.in_(
                    [
                        m.Match.player_1_match_data_id,
                        m.Match.player_2_match_data_id,
                        m.Match.player_3_match_data_id,
                    ]
                ),
            )
        )
        .where(mpd1.c.slot_a_weapon_id.isnot(None))
    )

    mpd2 = m.MatchPlayerData.__table__.alias("mpd2")
    weapon_presence_b = (
        sa.select(
            m.Match.id.label("match_id"),
            mpd2.c.slot_b_weapon_id.label("weapon_id"),
        )
        .select_from(
            m.Match.__table__.join(
                mpd2,
                mpd2.c.id.in_(
                    [
                        m.Match.player_1_match_data_id,
                        m.Match.player_2_match_data_id,
                        m.Match.player_3_match_data_id,
                    ]
                ),
            )
        )
        .where(mpd2.c.slot_b_weapon_id.isnot(None))
    )

    weapon_match = sa.union(weapon_presence, weapon_presence_b).subquery("weapon_match")

    # Join weapon-presence to match-level data
    joined = (
        sa.select(
            weapon_match.c.weapon_id,
            match_kda.c.match_id,
            match_kda.c.wl_status,
            match_kda.c.date,
            match_kda.c.playtime,
            match_kda.c.kills,
            match_kda.c.deaths,
            match_kda.c.assists,
        )
        .select_from(
            weapon_match.join(
                match_kda, weapon_match.c.match_id == match_kda.c.match_id
            )
        )
        .subquery("joined")
    )

    w = m.Weapon.__table__.alias("w")

    query = (
        sa.select(
            joined.c.weapon_id,
            w.c.name.label("weapon_name"),
            sa.func.count().label("total_matches"),
            sa.func.count().filter(joined.c.wl_status == "win").label("win"),
            sa.func.count().filter(joined.c.wl_status == "lose").label("lose"),
            sa.func.count().filter(joined.c.wl_status == "flee").label("flee"),
            sa.func.round(
                sa.cast(
                    sa.func.count().filter(joined.c.wl_status == "win"),
                    sa.Numeric,
                )
                / sa.func.nullif(sa.func.count(), 0)
                * 100,
                3,
            ).label("win_ratio_percent"),
            sa.func.min(joined.c.date).label("first_match_date"),
            sa.func.max(joined.c.date).label("last_match_date"),
            sa.func.percentile_cont(0.5)
            .within_group(joined.c.playtime)
            .label("median_playtime"),
            sa.func.coalesce(sa.func.sum(joined.c.kills), 0).label("kills_sum"),
            sa.func.coalesce(sa.func.sum(joined.c.deaths), 0).label("deaths_sum"),
            sa.func.coalesce(sa.func.sum(joined.c.assists), 0).label("assists_sum"),
        )
        .select_from(joined.join(w, joined.c.weapon_id == w.c.id))
        .group_by(joined.c.weapon_id, w.c.name)
        .order_by(joined.c.weapon_id)
    )

    rows = (await session.execute(query)).fetchall()

    return [
        WeaponStats(
            weapon_id=row.weapon_id,
            weapon_name=row.weapon_name,
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
