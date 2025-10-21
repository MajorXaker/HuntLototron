from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio.session import AsyncSession
import models.enums.weapon_modifiers as mod

service_router = APIRouter(prefix="/service", tags=["service"])


@service_router.get(
    "/modification-types",
)
async def get_modification_types():
    data = {
        "ammo_size": [i for i in mod.AmmoSizeEnum],
        "sights": [i for i in mod.SightsEnum],
        "melee": [i for i in mod.MeleeEnum],
        "muzzle": [i for i in mod.MuzzleEnum],
        "magazine": [i for i in mod.MagazineEnum]
    }
    return data
