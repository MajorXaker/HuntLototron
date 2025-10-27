from typing import Annotated

import sqlalchemy as sa
from fastapi import APIRouter, status, Query, HTTPException
from sqlalchemy.dialects.postgresql import aggregate_order_by
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session_dep
from models import db_models as m
from models.enums.api import OrderingEnum
from models.schemas.match import (
    ShortMatchResponseSchema,
    CreateMatchResultSchema,
    GetMatchesSchema,
    FullMatchSchema,
    NewMatchSchema,
)

match_router = APIRouter(prefix="/matches", tags=["Matches"])


@match_router.post(
    "", response_model=ShortMatchResponseSchema, status_code=status.HTTP_201_CREATED
)
async def create_new_match(
    new_match_data: NewMatchSchema,
    db: AsyncSession = get_session_dep,
):
    match_player_data_id = await db.scalar(
        sa.insert(m.MatchPlayerData)
        .values(
            {
                m.MatchPlayerData.player_id: new_match_data.player_1_id,
                m.MatchPlayerData.slot_a_weapon_id: new_match_data.slot_a_weapon_id,
                m.MatchPlayerData.slot_a_ammo_a_id: new_match_data.slot_a_ammo_a_id,
                m.MatchPlayerData.slot_a_ammo_b_id: new_match_data.slot_a_ammo_b_id,
                m.MatchPlayerData.slot_a_dual_wielding: new_match_data.slot_a_dual_wielding,
                m.MatchPlayerData.slot_b_weapon_id: new_match_data.slot_b_weapon_id,
                m.MatchPlayerData.slot_b_ammo_a_id: new_match_data.slot_b_ammo_a_id,
                m.MatchPlayerData.slot_b_ammo_b_id: new_match_data.slot_b_ammo_b_id,
                m.MatchPlayerData.slot_b_dual_wielding: new_match_data.slot_b_dual_wielding,
            }
        )
        .returning(m.MatchPlayerData.id)
    )

    new_match_id = await db.scalar(
        sa.insert(m.Match)
        .values(
            {
                m.Match.date: new_match_data.date,
                m.Match.player_1_id: new_match_data.player_1_id,
                m.Match.player_2_id: new_match_data.player_2_id,
                m.Match.player_3_id: new_match_data.player_3_id,
                m.Match.player_1_match_data_id: match_player_data_id,
            }
        )
        .returning(m.Match.id)
    )

    return ShortMatchResponseSchema(match_id=new_match_id)


@match_router.post(
    "/results",
    response_model=ShortMatchResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_results(
    results_data: CreateMatchResultSchema,
    db: AsyncSession = get_session_dep,
):
    # check if match exists
    match_id = await db.scalar(
        sa.select(m.Match.id).where(m.Match.id == results_data.match_id)
    )
    if not match_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    player_match_data_id = await db.scalar(
        sa.update(m.Match)
        .where(m.Match.id == results_data.match_id)
        .values(
            {
                m.Match.wl_status: results_data.wl_status,
                m.Match.playtime: results_data.playtime,
                m.Match.kills_total: results_data.kills_total,
                m.Match.map_id: results_data.map_id,
            }
        )
        .returning(m.Match.player_1_match_data_id)
    )

    await db.execute(
        sa.delete(m.M2MFightLocations).where(m.M2MFightLocations.match_id == match_id)
    )

    fights_data = [
        {
            "match_id": results_data.match_id,
            "compound_id": fight_location_id,
            "fight_ordering": n,
        }
        for n, fight_location_id in enumerate(results_data.fights_places_ids)
    ]
    await db.execute(sa.insert(m.M2MFightLocations), fights_data)

    await db.execute(
        sa.update(m.MatchPlayerData)
        .values(
            {
                m.MatchPlayerData.kills: results_data.kills,
                m.MatchPlayerData.assists: results_data.assists,
                m.MatchPlayerData.deaths: results_data.deaths,
                m.MatchPlayerData.bounty: results_data.bounty,
            }
        )
        .where(m.MatchPlayerData.id == player_match_data_id)
    )

    return ShortMatchResponseSchema(match_id=results_data.match_id)


async def _get_matches(
    session: AsyncSession,
    match_id: int = None,
    ordering: OrderingEnum = OrderingEnum.DESC,
    limit: int = 50,
    offset: int = 0,
) -> list[FullMatchSchema]:
    match_data_raw_q = sa.select(
        m.MatchPlayerData.id,
        m.MatchPlayerData.player_id,
        m.MatchPlayerData.kills,
        m.MatchPlayerData.deaths,
        m.MatchPlayerData.assists,
        m.MatchPlayerData.bounty,
        m.MatchPlayerData.slot_a_weapon_id,
        m.MatchPlayerData.slot_a_ammo_a_id,
        m.MatchPlayerData.slot_a_ammo_b_id,
        m.MatchPlayerData.slot_a_dual_wielding,
        m.MatchPlayerData.slot_b_weapon_id,
        m.MatchPlayerData.slot_b_ammo_a_id,
        m.MatchPlayerData.slot_b_ammo_b_id,
        m.MatchPlayerData.slot_b_dual_wielding,
    )
    player_1_data = match_data_raw_q.alias("player_1_data")
    player_2_data = match_data_raw_q.alias("player_2_data")
    player_3_data = match_data_raw_q.alias("player_3_data")

    def build_player_data_json(player_alias):
        """Build JSON object for player data"""
        args = []
        for col in m.MatchPlayerData.__table__.columns:
            args.extend([col.name, player_alias.c[col.name]])
        return sa.func.json_build_object(*args)

    compounds_subquery = (
        sa.select(
            m.M2MFightLocations.match_id,
            sa.func.array_agg(
                aggregate_order_by(
                    m.M2MFightLocations.compound_id, m.M2MFightLocations.fight_ordering
                )
            ).label("compound_ids"),
        ).group_by(m.M2MFightLocations.match_id)
    ).subquery("compounds")

    query = sa.select(
        m.Match.id,
        m.Match.date,
        m.Match.wl_status,
        m.Match.kills_total,
        m.Match.map_id,
        m.Match.playtime,
        m.Match.player_1_id,
        m.Match.player_2_id,
        m.Match.player_3_id,
        build_player_data_json(player_1_data).label("player_1_data"),
        build_player_data_json(player_2_data).label("player_2_data"),
        build_player_data_json(player_3_data).label("player_3_data"),
        compounds_subquery.c.compound_ids.label("fight_locations_ids"),
    ).select_from(
        sa.outerjoin(
            m.Match, player_1_data, m.Match.player_1_match_data_id == player_1_data.c.id
        )
        .outerjoin(player_2_data, m.Match.player_2_match_data_id == player_2_data.c.id)
        .outerjoin(player_3_data, m.Match.player_3_match_data_id == player_3_data.c.id)
        .outerjoin(compounds_subquery, m.Match.id == compounds_subquery.c.match_id)
    )

    if match_id:
        query = query.where(m.Match.id == match_id)

    query = query.limit(limit).offset(offset)

    if ordering == OrderingEnum.DESC:
        query = query.order_by(
            m.Match.date.desc(),
            m.Match.id.desc(),
        )
    else:
        query = query.order_by(
            m.Match.date.asc(),
            m.Match.id.asc(),
        )

    data = (await session.execute(query)).fetchall()

    results = [
        FullMatchSchema(
            id=match.id,
            wl_status=match.wl_status,
            date=match.date,
            kills_total=match.kills_total,
            playtime=match.playtime.total_seconds() if match.playtime else None,
            map_id=match.map_id,
            fights_places_ids=match.fight_locations_ids,
            player_1_id=match.player_1_id,
            player_2_id=match.player_2_id,
            player_3_id=match.player_3_id,
            player_1_data=match.player_1_data,
            player_2_data=match.player_2_data if match.player_2_data["id"] else None,
            player_3_data=match.player_3_data if match.player_3_data["id"] else None,
        )
        for match in data
    ]

    return results


@match_router.get(
    "",
    response_model=GetMatchesSchema,
)
async def get_matches(
    ordering: OrderingEnum = OrderingEnum.DESC,
    limit: Annotated[int | None, Query(ge=1, le=100)] = 50,
    offset: Annotated[int | None, Query(ge=0)] = 0,
    db: AsyncSession = get_session_dep,
):
    res = await _get_matches(
        session=db,
        match_id=None,
        ordering=ordering,
        limit=limit,
        offset=offset,
    )
    return GetMatchesSchema(data=res)


@match_router.get(
    "/specific/{match_id}",
    response_model=GetMatchesSchema,
)
async def get_specific_matches(
    match_id: int,
    db: AsyncSession = get_session_dep,
):
    match_id = await db.scalar(sa.select(m.Match.id).where(m.Match.id == match_id))
    if not match_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    res = await _get_matches(
        match_id=match_id,
        session=db,
    )
    return GetMatchesSchema(data=res)


@match_router.delete(
    "/{match_id}",
    response_model=ShortMatchResponseSchema,
)
async def remove_matches(
    match_id: int,
    db: AsyncSession = get_session_dep,
):
    match_id = await db.scalar(sa.select(m.Match.id).where(m.Match.id == match_id))
    if not match_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    match_player_data_ids = (
        (
            await db.execute(
                sa.delete(m.Match)
                .where(m.Match.id == match_id)
                .returning(
                    m.Match.player_1_match_data_id,
                    m.Match.player_2_match_data_id,
                    m.Match.player_3_match_data_id,
                )
            )
        )
        .scalars()
        .all()
    )
    await db.execute(
        sa.delete(m.M2MFightLocations).where(m.M2MFightLocations.match_id == match_id)
    )
    await db.execute(
        sa.delete(m.MatchPlayerData).where(
            m.MatchPlayerData.id.in_(match_player_data_ids)
        )
    )
    return ShortMatchResponseSchema(match_id=match_id)
