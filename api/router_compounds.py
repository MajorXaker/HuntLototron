from typing import List

import sqlalchemy as sa
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session_dep
from models import db_models as m
from models.schemas.compound import CompoundCreate, CompoundResponse, CompoundUpdate

compound_router = APIRouter(prefix="/compounds", tags=["Compounds"])


@compound_router.get("", response_model=List[CompoundResponse])
async def get_compounds(
    skip: int = 0,
    limit: int = 100,
    map_id: int = None,
    db: AsyncSession = get_session_dep,
):
    """Get all compounds with pagination"""
    q = sa.select(m.Compound).offset(skip).limit(limit)

    if map_id:
        q = q.where(m.Compound.map_id == map_id)

    result = await db.execute(q)
    compounds = result.scalars().all()
    return compounds


@compound_router.get("/{compound_id}", response_model=CompoundResponse)
async def get_compound(compound_id: int, db: AsyncSession = get_session_dep):
    """Get a specific compound by _id"""
    result = await db.execute(sa.select(m.Compound).where(m.Compound.id == compound_id))
    compound = result.scalar_one_or_none()

    if not compound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compound with name '{compound_id}' not found",
        )

    return compound


@compound_router.post(
    "", response_model=CompoundResponse, status_code=status.HTTP_201_CREATED
)
async def create_compound(
    compound_data: CompoundCreate, db: AsyncSession = get_session_dep
):
    """Create a new compound"""
    # Check if compound already exists
    result = await db.execute(
        sa.select(m.Compound).where(
            m.Compound.name == compound_data.name,
            m.Compound.map_id == compound_data.map_id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Compound with name '{compound_data.name}' already exists on selected map",
        )

    # Insert new compound
    result = await db.execute(
        sa.insert(m.Compound)
        .values(
            {
                m.Compound.name: compound_data.name,
                m.Compound.map_id: compound_data.map_id,
                m.Compound.double_clue: compound_data.double_clue,
            }
        )
        .returning(m.Compound)
    )
    compound = result.scalar_one()

    return compound


@compound_router.patch("/{compound_id}", response_model=CompoundResponse)
async def update_compound(
    compound_id: int, compound_data: CompoundUpdate, db: AsyncSession = get_session_dep
):
    """Update a compound by its id"""
    # Check if compound exists
    result = await db.execute(sa.select(m.Compound).where(m.Compound.id == compound_id))
    compound = result.scalar_one_or_none()

    if not compound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compound with name '{compound_id}' not found",
        )

    # Update only provided fields
    update_data = compound_data.model_dump(exclude_unset=True)
    if update_data:
        result = await db.execute(
            sa.update(m.Compound)
            .where(m.Compound.id == compound_id)
            .values(**update_data)
            .returning(m.Compound)
        )
        compound = result.scalar_one()

    return compound


@compound_router.delete("/{compound_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_compound(compound_id: int, db: AsyncSession = get_session_dep):
    """Delete a compound"""
    result = await db.execute(sa.delete(m.Compound).where(m.Compound.id == compound_id))

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compound with name '{compound_id}' not found",
        )
