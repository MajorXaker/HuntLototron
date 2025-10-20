from typing import List

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


from db import get_session_dep
from models import db_models as m
from models.schemas.compound import CompoundCreate, CompoundUpdate, CompoundResponse

compound_router = APIRouter(prefix="/compounds", tags=["Compounds"])


@compound_router.get("", response_model=List[CompoundResponse])
async def get_compounds(
    skip: int = 0, limit: int = 100, db: AsyncSession = get_session_dep
):
    """Get all compounds with pagination"""
    result = await db.execute(sa.select(m.Compound).offset(skip).limit(limit))
    compounds = result.scalars().all()
    return compounds


@compound_router.get("/{name}", response_model=CompoundResponse)
async def get_compound(name: str, db: AsyncSession = get_session_dep):
    """Get a specific compound by name"""
    result = await db.execute(sa.select(m.Compound).where(m.Compound.name == name))
    compound = result.scalar_one_or_none()

    if not compound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compound with name '{name}' not found",
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
        sa.select(m.Compound).where(m.Compound.name == compound_data.name)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Compound with name '{compound_data.name}' already exists",
        )

    # Insert new compound
    result = await db.execute(
        sa.insert(m.Compound).values(**compound_data.model_dump()).returning(m.Compound)
    )
    compound = result.scalar_one()

    return compound


@compound_router.patch("/{name}", response_model=CompoundResponse)
async def update_compound(
    name: str, compound_data: CompoundUpdate, db: AsyncSession = get_session_dep
):
    """Update a compound"""
    # Check if compound exists
    result = await db.execute(sa.select(m.Compound).where(m.Compound.name == name))
    compound = result.scalar_one_or_none()

    if not compound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compound with name '{name}' not found",
        )

    # Update only provided fields
    update_data = compound_data.model_dump(exclude_unset=True)
    if update_data:
        result = await db.execute(
            sa.update(m.Compound)
            .where(m.Compound.name == name)
            .values(**update_data)
            .returning(m.Compound)
        )
        compound = result.scalar_one()

    return compound


@compound_router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_compound(name: str, db: AsyncSession = get_session_dep):
    """Delete a compound"""
    result = await db.execute(sa.delete(m.Compound).where(m.Compound.name == name))

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compound with name '{name}' not found",
        )
