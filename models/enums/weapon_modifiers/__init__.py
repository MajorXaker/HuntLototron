# ruff:noqa: F401
from enum import StrEnum

from .sights_enum import SightsEnum
from .meelee_modifier_enum import MeleeEnum
from .magazine_modifier import MagazineEnum
from .ammo_size import AmmoSizeEnum
from .muzzle_device_enum import MuzzleEnum
from .weapon_size import WeaponSizeEnum
# TODO semi avto and avto variants

class DefaultModsEnum(StrEnum):
    DEFAULT_SIGHTS = SightsEnum.IRON
    DEFAULT_MELEE = MeleeEnum.REGULAR
    DEFAULT_MAGAZINE = MagazineEnum.REGULAR
    DEFAULT_MUZZLE = MuzzleEnum.REGULAR
    DEFAULT_WEAPON_SIZE = WeaponSizeEnum.REGULAR
