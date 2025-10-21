from typing import List

import sqlalchemy as sa
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session_dep
from models import db_models as m
from models.schemas.map import MapCreate, MapResponse

map_router = APIRouter(prefix="/maps", tags=["Maps"])


@map_router.get("", response_model=List[MapResponse])
async def get_maps(db: AsyncSession = get_session_dep):
    """Get all maps"""
    result = await db.execute(sa.select(m.Map))
    maps = result.scalars().all()
    return maps


@map_router.get("/{map_id}", response_model=MapResponse)
async def get_map(map_id: int, db: AsyncSession = get_session_dep):
    """Get a specific map by id"""
    result = await db.execute(sa.select(m.Map).where(m.Map.id == map_id))
    map_obj = result.scalar_one_or_none()

    if not map_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Map with name '{map_id}' not found",
        )

    return map_obj


@map_router.post("", response_model=MapResponse, status_code=status.HTTP_201_CREATED)
async def create_map(map_data: MapCreate, db: AsyncSession = get_session_dep):
    """Create a new map"""
    # Check if map already exists
    result = await db.execute(sa.select(m.Map).where(m.Map.name == map_data.name))
    existing_map = result.scalar_one_or_none()

    if existing_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Map with name '{map_data.name}' already exists",
        )

    # Insert new map
    result = await db.execute(
        sa.insert(m.Map).values(name=map_data.name).returning(m.Map)
    )
    map_obj = result.scalar_one()

    return map_obj


@map_router.delete("/{map_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_map(map_id: int, db: AsyncSession = get_session_dep):
    """Delete a map"""
    result = await db.scalar(
        sa.delete(m.Map).where(m.Map.id == map_id).returning(m.Map.id)
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Map with id '{map_id}' is not found",
        )
