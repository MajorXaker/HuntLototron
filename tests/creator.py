from datetime import date, timedelta

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

import models.db_models as m
import models.enums.weapon_modifiers as mod
from models.enums.gamemode import GameModeEnum


class Creator:
    """Helper class to create test data"""

    def __init__(self, session: AsyncSession):
        self.session = session

        self.created_weapon_types_ids = {}
        self.created_weapons_ids = {}

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
        if name in self.created_weapon_types_ids:
            return self.created_weapon_types_ids[name]
        weapon_id = await self.session.scalar(
            sa.insert(m.WeaponType).values(name=name).returning(m.WeaponType.id)
        )
        self.created_weapon_types_ids[name] = weapon_id
        return weapon_id

    async def create_weapon(
        self,
        name: str,
        weapon_type_id: int,
        core_gun_id: int = None,
        slot_size: int = 3,
        price: int = 100,
        sights: str = mod.DefaultModsEnum.DEFAULT_SIGHTS,
        melee: str = mod.DefaultModsEnum.DEFAULT_MELEE,
        muzzle: str = mod.DefaultModsEnum.DEFAULT_MUZZLE,
        magazine: str = mod.DefaultModsEnum.DEFAULT_MAGAZINE,
        ammo_size: mod.AmmoSizeEnum = mod.AmmoSizeEnum.COMPACT,
        has_ammo_B: bool = False,
    ) -> int:
        if name in self.created_weapons_ids:
            return self.created_weapons_ids[name]
        weapon_id = await self.session.scalar(
            sa.insert(m.Weapon)
            .values(
                name=name,
                weapon_type_id=weapon_type_id,
                core_gun_id=core_gun_id,
                slot_size=slot_size,
                price=price,
                sights=sights,
                melee=melee,
                muzzle=muzzle,
                magazine=magazine,
                has_ammo_B=has_ammo_B,
                ammo_size=ammo_size,
                weapon_size=mod.WeaponSizeEnum.REGULAR,
            )
            .returning(m.Weapon.id)
        )
        self.created_weapons_ids[name] = weapon_id
        return weapon_id

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

    async def create_match_player_data(
        self,
        player_id: int,
        slot_a_weapon_id: int,
        slot_b_weapon_id: int,
        slot_a_ammo_a_id: int = None,
        slot_a_ammo_b_id: int = None,
        slot_a_dual_wielding: bool = False,
        slot_b_ammo_a_id: int = None,
        slot_b_ammo_b_id: int = None,
        slot_b_dual_wielding: bool = False,
        kills: int = 0,
        assists: int = 0,
        deaths: int = 0,
        bounty: int = 0,
    ) -> int:
        """Create match player data and return its ID"""
        return await self.session.scalar(
            sa.insert(m.MatchPlayerData)
            .values(
                player_id=player_id,
                slot_a_weapon_id=slot_a_weapon_id,
                slot_a_ammo_a_id=slot_a_ammo_a_id,
                slot_a_ammo_b_id=slot_a_ammo_b_id,
                slot_a_dual_wielding=slot_a_dual_wielding,
                slot_b_weapon_id=slot_b_weapon_id,
                slot_b_ammo_a_id=slot_b_ammo_a_id,
                slot_b_ammo_b_id=slot_b_ammo_b_id,
                slot_b_dual_wielding=slot_b_dual_wielding,
                kills=kills,
                assists=assists,
                deaths=deaths,
                bounty=bounty,
            )
            .returning(m.MatchPlayerData.id)
        )

    async def create_match(
        self,
        player_1_id: int,
        player_1_match_data_id: int = None,
        wl_status: str = None,
        match_date: date = None,
        kills_total: int = 0,
        playtime=None,
        map_id: int = None,
        player_2_id: int = None,
        player_2_match_data_id: int = None,
        player_3_id: int = None,
        player_3_match_data_id: int = None,
        game_mode: GameModeEnum = GameModeEnum.HUNT,
    ) -> int:
        """Create a match and return its ID"""

        if match_date is None:
            match_date = date.today()
        if playtime is None:
            playtime = timedelta(minutes=20)

        if not player_1_match_data_id:
            player_1_match_data_id = await self.create_match_player_data(
                player_id=player_1_id,
                slot_a_weapon_id=await self.create_weapon(
                    name="boomstick",
                    weapon_type_id=await self.create_weapon_type("pistol"),
                ),
                slot_b_weapon_id=await self.create_weapon(
                    name="broomstick",
                    weapon_type_id=await self.create_weapon_type("rifle"),
                ),
            )

        return await self.session.scalar(
            sa.insert(m.Match)
            .values(
                wl_status=wl_status,
                date=match_date,
                kills_total=kills_total,
                playtime=playtime,
                map_id=map_id,
                player_1_id=player_1_id,
                player_2_id=player_2_id,
                player_3_id=player_3_id,
                player_1_match_data_id=player_1_match_data_id,
                player_2_match_data_id=player_2_match_data_id,
                player_3_match_data_id=player_3_match_data_id,
                game_mode=game_mode,
            )
            .returning(m.Match.id)
        )

    async def create_fight_location(
        self,
        match_id: int,
        compound_id: int,
        fight_ordering: int = 0,
    ) -> None:
        """Create a fight location entry"""
        await self.session.execute(
            sa.insert(m.M2MFightLocations).values(
                match_id=match_id,
                compound_id=compound_id,
                fight_ordering=fight_ordering,
            )
        )
