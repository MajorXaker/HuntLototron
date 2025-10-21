from typing import List

import sqlalchemy as sa
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session_dep
from models import db_models as m
from models.schemas.player import PlayerCreate, PlayerUpdate, PlayerResponse

player_router = APIRouter(prefix="/players", tags=["Players"])


@player_router.get("", response_model=List[PlayerResponse])
async def get_players(
    skip: int = 0, limit: int = 100, db: AsyncSession = get_session_dep
):
    """Get all players with pagination"""
    result = await db.execute(sa.select(m.Player).offset(skip).limit(limit))
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

    # Update only provided fields
    update_data = player_data.model_dump(exclude_unset=True)
    if update_data:
        result = await db.execute(
            sa.update(m.Player)
            .where(m.Player.id == player_id)
            .values(**update_data)
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
