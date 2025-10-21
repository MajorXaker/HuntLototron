import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

import models.db_models as m
import models.enums.weapon_modifiers as mod


class Creator:
    """Helper class to create test data"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_map(self, name: str = "TestMap") -> int:
        """Create a test map and return its name (PK)"""
        return await self.session.scalar(
            sa.insert(m.Map).values(name=name).returning(m.Map.id)
        )

    async def create_compound(
        self,
        name: str = "TestCompound",
        map_id: int = None,
        double_clue: bool = False,
        x_relative: float = 10.0,
        y_relative: float = 20.0,
    ) -> int:
        """Create a test compound and return its name (PK)"""
        if not map_id:
            map_id = await self.create_map(name)

        return await self.session.scalar(
            sa.insert(m.Compound)
            .values(
                name=name,
                map_id=map_id,
                double_clue=double_clue,
                x_relative=x_relative,
                y_relative=y_relative,
            )
            .returning(m.Compound.id)
        )

    async def create_weapon_type(self, name: str = "TestWeaponType") -> int:
        """Create a test weapon type and return its ID"""
        return await self.session.scalar(
            sa.insert(m.WeaponType).values(name=name).returning(m.WeaponType.id)
        )

    async def create_weapon(
        self,
        name: str,
        weapon_type_id: int,
        core_gun_id: int = None,
        size: int = 3,
        price: int = 100,
        sights: str = mod.DefaultModsEnum.DEFAULT_SIGHTS,
        melee: str = mod.DefaultModsEnum.DEFAULT_MELEE,
        muzzle: str = mod.DefaultModsEnum.DEFAULT_MUZZLE,
        magazine: str = mod.DefaultModsEnum.DEFAULT_MAGAZINE,
        has_ammo_B: bool = False,
    ) -> int:
        """Create a test weapon and return its ID"""
        return await self.session.scalar(
            sa.insert(m.Weapon)
            .values(
                name=name,
                weapon_type_id=weapon_type_id,
                core_gun_id=core_gun_id,
                size=size,
                price=price,
                sights=sights,
                melee=melee,
                muzzle=muzzle,
                magazine=magazine,
                has_ammo_B=has_ammo_B,
                ammo_size=mod.AmmoSizeEnum.COMPACT,
            )
            .returning(m.Weapon.id)
        )

    async def create_ammo_type(self, name: str = "TestAmmo") -> int:
        """Create a test ammo type and return its ID"""
        return await self.session.scalar(
            sa.insert(m.AmmoType).values(name=name).returning(m.AmmoType.id)
        )

    async def create_player(
        self,
        username: str = "HuntieTheHunter",
    ) -> int:
        """Create a test player and return its ID"""
        return await self.session.scalar(
            sa.insert(m.Player).values(username=username).returning(m.Player.id)
        )
