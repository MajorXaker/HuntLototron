from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from db import get_session_dep
from models import db_models as m
from models.schemas.weapon_type import (
    WeaponTypeCreate,
    WeaponTypeUpdate,
    WeaponTypeResponse,
)

weapon_types_router = APIRouter(prefix="/weapon-types", tags=["Weapon Types"])


@weapon_types_router.get("", response_model=List[WeaponTypeResponse])
async def get_weapon_types(
    skip: int = 0, limit: int = 100, db: AsyncSession = get_session_dep
):
    """Get all weapon types with pagination"""
    result = await db.execute(
        sa.select(
            m.WeaponType.id,
            m.WeaponType.name,
        )
        .offset(skip)
        .limit(limit)
    )
    weapon_types = result.all()
    return weapon_types


@weapon_types_router.get("/{weapon_type_id}", response_model=WeaponTypeResponse)
async def get_weapon_type(weapon_type_id: int, db: AsyncSession = get_session_dep):
    """Get a specific weapon type by ID"""
    stmt = sa.select(m.WeaponType).where(m.WeaponType.id == weapon_type_id)
    result = await db.execute(stmt)
    weapon_type = result.scalar_one_or_none()

    if not weapon_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"WeaponType with id {weapon_type_id} not found",
        )

    return weapon_type


@weapon_types_router.post(
    "", response_model=WeaponTypeResponse, status_code=status.HTTP_201_CREATED
)
async def create_weapon_type(
    weapon_type_data: WeaponTypeCreate, db: AsyncSession = get_session_dep
):
    """Create a new weapon type"""
    typename = weapon_type_data.name
    if not typename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Name cannot be empty"
        )

    existing = await db.scalar(
        sa.select(m.WeaponType.id).where(m.WeaponType.name == typename)
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"WeaponType with name {typename} already exists",
        )

    insert_result = (
        await db.execute(
            sa.insert(m.WeaponType)
            .values(name=typename)
            .returning(m.WeaponType.id, m.WeaponType.name)
        )
    ).fetchone()

    return insert_result


@weapon_types_router.patch("/{weapon_type_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_weapon_type(
    weapon_type_id: int,
    weapon_type_data: WeaponTypeUpdate,
    db: AsyncSession = get_session_dep,
):
    """Update a weapon type"""
    # Get existing weapon type
    stmt = sa.select(m.WeaponType).where(m.WeaponType.id == weapon_type_id)
    result = await db.execute(stmt)
    weapon_type = result.scalar_one_or_none()

    if not weapon_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"WeaponType with id {weapon_type_id} not found",
        )

    # Update only provided fields
    update_data = weapon_type_data.model_dump(exclude_unset=True)
    if update_data:
        stmt = (
            sa.update(m.WeaponType)
            .where(m.WeaponType.id == weapon_type_id)
            .values(**update_data)
            .returning(m.WeaponType)
        )
        await db.execute(stmt)


@weapon_types_router.delete("/{weapon_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_weapon_type(weapon_type_id: int, db: AsyncSession = get_session_dep):
    """Delete a weapon type"""
    stmt = (
        sa.delete(m.WeaponType)
        .where(m.WeaponType.id == weapon_type_id)
        .returning(m.WeaponType.id)
    )
    result = await db.scalar(stmt)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"WeaponType with id {weapon_type_id} not found",
        )
