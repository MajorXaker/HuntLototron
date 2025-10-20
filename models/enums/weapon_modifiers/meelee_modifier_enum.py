from enum import StrEnum


class MeleeEnum(StrEnum):
    NO_DESIGNATED = "no_designated"  # just regular stock or nothing
    SELF = "self"  # when the weapon is actually melee (e.g. bomblance, machete)
    HATCHED = "hatchet"  # small weapon to act like a small hatchet
    TALON = "talon"  # full weapon swing to deal serious damage
    BAYONET = "bayonet"  # hard piercing variant, similar to previous
    MACE = "mace"  # blunt strike for small weapons
    KNUCKLES = "knuckles"  # same as previous but for pistols
