# ruff:noqa: F401
from enum import StrEnum

from .ammo_size import AmmoSizeEnum
from .magazine_modifier import MagazineEnum
from .meelee_modifier_enum import MeleeEnum
from .muzzle_device_enum import MuzzleEnum
from .sights_enum import SightsEnum
from .weapon_size import WeaponSizeEnum

# TODO semi avto and avto variants


class DefaultModsEnum(StrEnum):
    DEFAULT_SIGHTS = SightsEnum.IRON
    DEFAULT_MELEE = MeleeEnum.REGULAR
    DEFAULT_MAGAZINE = MagazineEnum.REGULAR
    DEFAULT_MUZZLE = MuzzleEnum.REGULAR
    DEFAULT_WEAPON_SIZE = WeaponSizeEnum.REGULAR
