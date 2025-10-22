from enum import StrEnum


class WeaponSizeEnum(StrEnum):
    REGULAR = "regular"
    STOCK = "stock" # pistol with additional stock, like bornheim match
    CARBINE = "carbine"
    # that's either lemat carbine or mosin carbine
    # first is extended stock and barrel, other is shortened
    # so doublesided
    SHORTENED = "shortened" # cut versions of rifles and shotguns
    PISTOL = "pistol" # extremely short version of a rifle->pistol conversion
    EXTENDED = "extended" # additional barrel length
