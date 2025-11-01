from typing import List

import sqlalchemy as sa
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session_dep
from models import db_models as m
from models.enums.player_status import PlayerStatusEnum
from models.schemas.player import PlayerCreate, PlayerUpdate, PlayerResponse

player_router = APIRouter(prefix="/players", tags=["Players"])


@player_router.get("", response_model=List[PlayerResponse])
async def get_players(
    skip: int = 0,
    limit: int = 100,
    include_disabled: bool = False,
    db: AsyncSession = get_session_dep
):
    """Get all players with pagination"""
    query = sa.select(m.Player).offset(skip).limit(limit)

    if not include_disabled:
        query = query.where(m.Player.status == PlayerStatusEnum.ACTIVE)

    result = await db.execute(query)
    players = result.scalars().all()
    return players


@player_router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(player_id: int, db: AsyncSession = get_session_dep):
    """Get a specific player by ID"""
    result = await db.execute(sa.select(m.Player).where(m.Player.id == player_id))
    player = result.scalar_one_or_none()

    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with id {player_id} not found",
        )

    return player


@player_router.post(
    "", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED
)
async def create_player(player_data: PlayerCreate, db: AsyncSession = get_session_dep):
    """Create a new player"""

    if not player_data.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No username provided"
        )
    # Insert new player
    result = await db.execute(
        sa.insert(m.Player)
        .values({m.Player.username: player_data.username})
        .returning(m.Player)
    )
    player = result.scalar_one()

    return player


@player_router.patch("/{player_id}", response_model=PlayerResponse)
async def update_player(
    player_id: int, player_data: PlayerUpdate, db: AsyncSession = get_session_dep
):
    """Update a player"""
    # Check if player exists
    result = await db.execute(sa.select(m.Player).where(m.Player.id == player_id))
    player = result.scalar_one_or_none()

    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with id {player_id} not found",
        )

    update_data = {}
    if player_data.username:
        update_data[m.Player.username] = player_data.username

    if player_data.is_disabled is not None:
        disabled_map = {
            True: PlayerStatusEnum.INACTIVE,
            False: PlayerStatusEnum.ACTIVE,
        }
        update_data[m.Player.status] = disabled_map[player_data.is_disabled]

    # Update only provided fields
    if update_data:
        result = await db.execute(
            sa.update(m.Player)
            .where(m.Player.id == player_id)
            .values(update_data)
            .returning(m.Player)
        )
        player = result.scalar_one()

    return player


@player_router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(player_id: int, db: AsyncSession = get_session_dep):
    """Delete a player"""
    result = await db.execute(sa.delete(m.Player).where(m.Player.id == player_id))

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with id {player_id} not found",
        )
