from typing import List

import sqlalchemy as sa
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session_dep
from models import db_models as m
from models.schemas.ammo_type import AmmoTypeCreate, AmmoTypeResponse, AmmoTypeUpdate

ammo_type_router = APIRouter(prefix="/ammo-types", tags=["Ammo Types"])


@ammo_type_router.get("", response_model=List[AmmoTypeResponse])
async def get_ammo_types(
    skip: int = 0, limit: int = 100, db: AsyncSession = get_session_dep
):
    """Get all ammo types with pagination"""
    result = await db.execute(sa.select(m.AmmoType).offset(skip).limit(limit))
    ammo_types = result.scalars().all()
    return ammo_types


@ammo_type_router.get("/{ammo_type_id}", response_model=AmmoTypeResponse)
async def get_ammo_type(ammo_type_id: int, db: AsyncSession = get_session_dep):
    """Get a specific ammo type by ID"""
    result = await db.execute(
        sa.select(m.AmmoType).where(m.AmmoType.id == ammo_type_id)
    )
    ammo_type = result.scalar_one_or_none()

    if not ammo_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AmmoType with id {ammo_type_id} not found",
        )

    return ammo_type


@ammo_type_router.post(
    "", response_model=AmmoTypeResponse, status_code=status.HTTP_201_CREATED
)
async def create_ammo_type(
    ammo_type_data: AmmoTypeCreate, db: AsyncSession = get_session_dep
):
    """Create a new ammo type"""
    # Insert new ammo type
    result = await db.execute(
        sa.insert(m.AmmoType)
        .values(**ammo_type_data.model_dump())
        .returning(m.AmmoType)
    )
    ammo_type = result.scalar_one()

    return ammo_type


@ammo_type_router.patch("/{ammo_type_id}", response_model=AmmoTypeResponse)
async def update_ammo_type(
    ammo_type_id: int,
    ammo_type_data: AmmoTypeUpdate,
    db: AsyncSession = get_session_dep,
):
    """Update an ammo type"""
    # Check if ammo type exists
    result = await db.execute(
        sa.select(m.AmmoType).where(m.AmmoType.id == ammo_type_id)
    )
    ammo_type = result.scalar_one_or_none()

    if not ammo_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AmmoType with id {ammo_type_id} not found",
        )

    # Update only provided fields
    update_data = ammo_type_data.model_dump(exclude_unset=True)
    if update_data:
        result = await db.execute(
            sa.update(m.AmmoType)
            .where(m.AmmoType.id == ammo_type_id)
            .values(**update_data)
            .returning(m.AmmoType)
        )
        ammo_type = result.scalar_one()

    return ammo_type


@ammo_type_router.delete("/{ammo_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ammo_type(ammo_type_id: int, db: AsyncSession = get_session_dep):
    """Delete an ammo type"""
    result = await db.execute(
        sa.delete(m.AmmoType).where(m.AmmoType.id == ammo_type_id)
    )

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AmmoType with id {ammo_type_id} not found",
        )
