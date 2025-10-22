from typing import List

import sqlalchemy as sa
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session_dep
from models import db_models as m
from models.schemas.weapon import WeaponResponse, WeaponCreate, WeaponUpdate
from models.enums import weapon_modifiers as mod

weapons_router = APIRouter(prefix="/weapons", tags=["Weapons"])


@weapons_router.get("", response_model=List[WeaponResponse])
async def get_weapons(
    skip: int = 0,
    limit: int = 100,
    ammo_size: mod.AmmoSizeEnum = None,
    core_gun_id: int = None,
    core_gun_only: bool = False,
    db: AsyncSession = get_session_dep,
):
    """Get all weapons with pagination"""
    query = sa.select(m.Weapon).offset(skip).limit(limit)

    if ammo_size:
        query = query.where(m.Weapon.ammo_size == ammo_size)
    if core_gun_id:
        query = query.where(
            sa.or_(
                m.Weapon.core_gun_id == core_gun_id,
                m.Weapon.id == core_gun_id,
            )
        )
    if core_gun_only:
        query = query.where(m.Weapon.core_gun_id.is_(None))

    result = await db.execute(query)

    weapons = result.scalars().all()
    return weapons


@weapons_router.get("/{weapon_id}", response_model=WeaponResponse)
async def get_weapon(weapon_id: int, db: AsyncSession = get_session_dep):
    """Get a specific weapon by ID"""
    result = await db.execute(sa.select(m.Weapon).where(m.Weapon.id == weapon_id))
    weapon = result.scalar_one_or_none()

    if not weapon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weapon with id {weapon_id} not found",
        )

    return weapon


@weapons_router.post(
    "", response_model=WeaponResponse, status_code=status.HTTP_201_CREATED
)
async def create_weapon(weapon_data: WeaponCreate, db: AsyncSession = get_session_dep):
    """Create a new weapon"""
    # Check if weapon with same name exists
    result = await db.execute(
        sa.select(m.Weapon).where(m.Weapon.name == weapon_data.name)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Weapon with name '{weapon_data.name}' already exists",
        )

    # Insert new weapon
    result = await db.execute(
        sa.insert(m.Weapon).values(**weapon_data.model_dump()).returning(m.Weapon)
    )
    weapon = result.scalar_one()

    return weapon


@weapons_router.patch("/{weapon_id}", response_model=WeaponResponse)
async def update_weapon(
    weapon_id: int, weapon_data: WeaponUpdate, db: AsyncSession = get_session_dep
):
    """Update a weapon"""
    # Check if weapon exists
    result = await db.execute(sa.select(m.Weapon).where(m.Weapon.id == weapon_id))
    weapon = result.scalar_one_or_none()

    if not weapon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weapon with id {weapon_id} not found",
        )

    # Update only provided fields
    update_data = weapon_data.model_dump(exclude_unset=True)
    if update_data:
        result = await db.execute(
            sa.update(m.Weapon)
            .where(m.Weapon.id == weapon_id)
            .values(**update_data)
            .returning(m.Weapon)
        )
        weapon = result.scalar_one()

    return weapon


@weapons_router.delete("/{weapon_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_weapon(weapon_id: int, db: AsyncSession = get_session_dep):
    """Delete a weapon"""
    result = await db.execute(sa.delete(m.Weapon).where(m.Weapon.id == weapon_id))

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weapon with id {weapon_id} not found",
        )
