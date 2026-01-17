import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from models import db_models as m
from models.dto.teammate_stats import TeamCompositionStats, TeammateStats


async def get_separate_teammates_stats(
    session: AsyncSession, matches_total: int
) -> list[TeammateStats]:
    # ---- general selects
    # Aliases for player joins
    p1 = m.Player.__table__.alias("p1")

    # Build the three SELECT branches for UNION ALL
    player_2_select = sa.select(
        m.Match.player_2_id.label("player_id"), m.Match.wl_status
    ).where(m.Match.player_2_id.isnot(None), m.Match.wl_status.isnot(None))

    player_3_select = sa.select(
        m.Match.player_3_id.label("player_id"), m.Match.wl_status
    ).where(m.Match.player_3_id.isnot(None), m.Match.wl_status.isnot(None))

    solo_player_select = sa.select(
        m.Match.player_1_id.label("player_id"), m.Match.wl_status
    ).where(
        m.Match.player_2_id.is_(None),
        m.Match.player_3_id.is_(None),
        m.Match.wl_status.isnot(None),
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
            match_share=tm.matches_sum / matches_total,
            total_matches=matches_total,
            winrate=tm.win_ratio_percent,
        )
        for tm in unique_teammates
    ]


async def get_teammate_composition_stats(
    session: AsyncSession, matches_total: int
) -> list[TeamCompositionStats]:
    p1 = m.Player.__table__.alias("p1")
    p2 = m.Player.__table__.alias("p2")

    # Build subquery for player pairs - handles both full pairs and single teammates
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
        )
        .where(
            sa.or_(m.Match.player_2_id.isnot(None), m.Match.player_3_id.isnot(None)),
            m.Match.wl_status.isnot(None),
            # Exclude solo matches (both NULL)
            sa.not_(
                sa.and_(m.Match.player_2_id.is_(None), m.Match.player_3_id.is_(None))
            ),
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
            match_share=tm.matches_sum / matches_total,
            total_matches=matches_total,
            winrate=tm.win_ratio_percent,
        )
        for tm in combinations
    ]
