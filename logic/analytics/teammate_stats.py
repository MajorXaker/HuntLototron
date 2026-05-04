import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from models import db_models as m
from models.dto.teammate_stats import TeamCompositionStats, TeammateStats
from models.enums.gamemode import GameModeEnum


async def get_separate_teammates_stats(
    session: AsyncSession,
    matches_total: int,
    game_mode: GameModeEnum = GameModeEnum.HUNT,
) -> list[TeammateStats]:
    # ---- general selects
    # Aliases for player joins
    p1 = m.Player.__table__.alias("p1")
    mpd2 = m.MatchPlayerData.__table__.alias("mpd2")
    mpd3 = m.MatchPlayerData.__table__.alias("mpd3")
    mpd_solo = m.MatchPlayerData.__table__.alias("mpd_solo")

    # Build the three SELECT branches for UNION ALL
    player_2_select = (
        sa.select(
            m.Match.player_2_id.label("player_id"),
            m.Match.wl_status,
            m.Match.date,
            m.Match.playtime,
            sa.func.coalesce(mpd2.c.kills, 0).label("kills"),
            sa.func.coalesce(mpd2.c.deaths, 0).label("deaths"),
            sa.func.coalesce(mpd2.c.assists, 0).label("assists"),
        )
        .select_from(
            m.Match.__table__.outerjoin(
                mpd2, mpd2.c.id == m.Match.player_2_match_data_id
            )
        )
        .where(
            m.Match.player_2_id.isnot(None),
            m.Match.wl_status.isnot(None),
            m.Match.game_mode == game_mode,
        )
    )

    player_3_select = (
        sa.select(
            m.Match.player_3_id.label("player_id"),
            m.Match.wl_status,
            m.Match.date,
            m.Match.playtime,
            sa.func.coalesce(mpd3.c.kills, 0).label("kills"),
            sa.func.coalesce(mpd3.c.deaths, 0).label("deaths"),
            sa.func.coalesce(mpd3.c.assists, 0).label("assists"),
        )
        .select_from(
            m.Match.__table__.outerjoin(
                mpd3, mpd3.c.id == m.Match.player_3_match_data_id
            )
        )
        .where(
            m.Match.player_3_id.isnot(None),
            m.Match.wl_status.isnot(None),
            m.Match.game_mode == game_mode,
        )
    )

    solo_player_select = (
        sa.select(
            m.Match.player_1_id.label("player_id"),
            m.Match.wl_status,
            m.Match.date,
            m.Match.playtime,
            sa.func.coalesce(mpd_solo.c.kills, 0).label("kills"),
            sa.func.coalesce(mpd_solo.c.deaths, 0).label("deaths"),
            sa.func.coalesce(mpd_solo.c.assists, 0).label("assists"),
        )
        .select_from(
            m.Match.__table__.outerjoin(
                mpd_solo, mpd_solo.c.id == m.Match.player_1_match_data_id
            )
        )
        .where(
            m.Match.player_2_id.is_(None),
            m.Match.player_3_id.is_(None),
            m.Match.wl_status.isnot(None),
            m.Match.game_mode == game_mode,
        )
    )

    # Combine with UNION ALL
    player_matches = sa.union_all(
        player_2_select, player_3_select, solo_player_select
    ).subquery("player_matches")

    # Main query with aggregations
    query = (
        sa.select(
            player_matches.c.player_id,
            p1.c.username,
            sa.func.count().label("total_matches"),
            sa.func.count().filter(player_matches.c.wl_status == "win").label("win"),
            sa.func.count().filter(player_matches.c.wl_status == "lose").label("lose"),
            sa.func.count().filter(player_matches.c.wl_status == "flee").label("flee"),
            sa.func.count(player_matches.c.player_id).label("matches_sum"),
            sa.func.round(
                sa.cast(
                    sa.func.count().filter(player_matches.c.wl_status == "win"),
                    sa.Numeric,
                )
                / sa.func.nullif(sa.func.count(), 0)
                * 100,
                3,
            ).label("win_ratio_percent"),
            sa.func.min(player_matches.c.date).label("first_match_date"),
            sa.func.max(player_matches.c.date).label("last_match_date"),
            sa.func.percentile_cont(0.5)
            .within_group(player_matches.c.playtime)
            .label("median_playtime"),
            sa.func.coalesce(sa.func.sum(player_matches.c.kills), 0).label("kills_sum"),
            sa.func.coalesce(sa.func.sum(player_matches.c.deaths), 0).label(
                "deaths_sum"
            ),
            sa.func.coalesce(sa.func.sum(player_matches.c.assists), 0).label(
                "assists_sum"
            ),
        )
        .select_from(player_matches.join(p1, player_matches.c.player_id == p1.c.id))
        .group_by(player_matches.c.player_id, p1.c.username)
        .order_by(player_matches.c.player_id)
    )

    unique_teammates = (await session.execute(query)).fetchall()

    return [
        TeammateStats(
            teammate_id=tm.player_id,
            teammate_name=tm.username,
            wins=tm.win,
            losses=tm.lose,
            flees=tm.flee,
            match_share=(tm.matches_sum / matches_total) * 100
            if matches_total
            else 0.0,
            total_matches=tm.matches_sum,
            winrate=tm.win_ratio_percent or 0.0,
            first_match=tm.first_match_date,
            last_match=tm.last_match_date,
            median_playtime_seconds=(
                tm.median_playtime.seconds if tm.median_playtime else 0.0
            ),
            kills=tm.kills_sum,
            deaths=tm.deaths_sum,
            assists=tm.assists_sum,
        )
        for tm in unique_teammates
    ]


async def get_teammate_composition_stats(
    session: AsyncSession,
    matches_total: int,
    game_mode: GameModeEnum = GameModeEnum.HUNT,
) -> list[TeamCompositionStats]:
    p1 = m.Player.__table__.alias("p1")
    p2 = m.Player.__table__.alias("p2")
    mpd2 = m.MatchPlayerData.__table__.alias("mpd2")
    mpd3 = m.MatchPlayerData.__table__.alias("mpd3")

    # Build subquery for player pairs - handles both full pairs and single teammates
    # K/D/A summed across both teammates' match_player_data (excluding player_1)
    player_pairs_select = (
        sa.select(
            sa.case(
                (m.Match.player_3_id.is_(None), m.Match.player_2_id),
                else_=sa.func.least(m.Match.player_2_id, m.Match.player_3_id),
            ).label("player_a_id"),
            sa.case(
                (m.Match.player_3_id.is_(None), sa.null()),
                else_=sa.func.greatest(m.Match.player_2_id, m.Match.player_3_id),
            ).label("player_b_id"),
            m.Match.wl_status,
            m.Match.date,
            m.Match.playtime,
            (
                sa.func.coalesce(mpd2.c.kills, 0) + sa.func.coalesce(mpd3.c.kills, 0)
            ).label("kills"),
            (
                sa.func.coalesce(mpd2.c.deaths, 0) + sa.func.coalesce(mpd3.c.deaths, 0)
            ).label("deaths"),
            (
                sa.func.coalesce(mpd2.c.assists, 0)
                + sa.func.coalesce(mpd3.c.assists, 0)
            ).label("assists"),
        )
        .select_from(
            m.Match.__table__.outerjoin(
                mpd2, mpd2.c.id == m.Match.player_2_match_data_id
            ).outerjoin(mpd3, mpd3.c.id == m.Match.player_3_match_data_id)
        )
        .where(
            sa.or_(m.Match.player_2_id.isnot(None), m.Match.player_3_id.isnot(None)),
            m.Match.wl_status.isnot(None),
            # Exclude solo matches (both NULL)
            sa.not_(
                sa.and_(m.Match.player_2_id.is_(None), m.Match.player_3_id.is_(None))
            ),
            m.Match.game_mode == game_mode,
        )
        .subquery("player_pairs")
    )

    # Main query with joins and aggregations
    query = (
        sa.select(
            player_pairs_select.c.player_a_id,
            p1.c.username.label("player_a_username"),
            player_pairs_select.c.player_b_id,
            p2.c.username.label("player_b_username"),
            sa.func.count().label("total_matches"),
            sa.func.count()
            .filter(player_pairs_select.c.wl_status == "win")
            .label("win"),
            sa.func.count()
            .filter(player_pairs_select.c.wl_status == "lose")
            .label("lose"),
            sa.func.count()
            .filter(player_pairs_select.c.wl_status == "flee")
            .label("flee"),
            sa.func.count(player_pairs_select.c.player_a_id).label("matches_sum"),
            sa.func.round(
                sa.cast(
                    sa.func.count().filter(player_pairs_select.c.wl_status == "win"),
                    sa.Numeric,
                )
                / sa.func.nullif(sa.func.count(), 0)
                * 100,
                2,
            ).label("win_ratio_percent"),
            sa.func.min(player_pairs_select.c.date).label("first_match_date"),
            sa.func.max(player_pairs_select.c.date).label("last_match_date"),
            sa.func.percentile_cont(0.5)
            .within_group(player_pairs_select.c.playtime)
            .label("median_playtime"),
            sa.func.coalesce(sa.func.sum(player_pairs_select.c.kills), 0).label(
                "kills_sum"
            ),
            sa.func.coalesce(sa.func.sum(player_pairs_select.c.deaths), 0).label(
                "deaths_sum"
            ),
            sa.func.coalesce(sa.func.sum(player_pairs_select.c.assists), 0).label(
                "assists_sum"
            ),
        )
        .select_from(
            player_pairs_select.join(
                p1, player_pairs_select.c.player_a_id == p1.c.id
            ).outerjoin(p2, player_pairs_select.c.player_b_id == p2.c.id)
        )
        .group_by(
            player_pairs_select.c.player_a_id,
            p1.c.username,
            player_pairs_select.c.player_b_id,
            p2.c.username,
        )
        .order_by(
            player_pairs_select.c.player_a_id,
            player_pairs_select.c.player_b_id.nulls_last(),
        )
    )

    combinations = (await session.execute(query)).fetchall()

    return [
        TeamCompositionStats(
            teammate_a_id=tm.player_a_id,
            teammate_a_name=tm.player_a_username,
            teammate_b_id=tm.player_b_id,
            teammate_b_name=tm.player_b_username,
            wins=tm.win,
            losses=tm.lose,
            flees=tm.flee,
            match_share=(tm.matches_sum / matches_total) * 100
            if matches_total
            else 0.0,
            total_matches=tm.matches_sum,
            winrate=tm.win_ratio_percent or 0.0,
            first_match=tm.first_match_date,
            last_match=tm.last_match_date,
            median_playtime_seconds=(
                tm.median_playtime.seconds if tm.median_playtime else 0.0
            ),
            kills=tm.kills_sum,
            deaths=tm.deaths_sum,
            assists=tm.assists_sum,
        )
        for tm in combinations
    ]
