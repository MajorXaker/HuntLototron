from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from models.enums import weapon_modifiers as mod


class WeaponBase(BaseModel):
    """Base weapon schema with validation"""

    name: str = Field(..., min_length=1, max_length=50, description="Weapon name")
    weapon_type_id: int = Field(..., gt=0, description="Foreign key to weapon type")
    core_gun_id: Optional[int] = Field(
        None, gt=0, description="Base weapon this is derived from"
    )

    slot_size: int = Field(
        ..., ge=1, le=3, description="Weapon size: 1=small, 2=medium, 3=large"
    )

    # Weapon modifications with enum validation
    sights: Optional[mod.SightsEnum] = Field(
        default=mod.DefaultModsEnum.DEFAULT_SIGHTS,
        description="Type of sights on the weapon",
    )
    melee: Optional[mod.MeleeEnum] = Field(
        default=mod.DefaultModsEnum.DEFAULT_MELEE,
        description="Type of melee attack available",
    )
    muzzle: Optional[mod.MuzzleEnum] = Field(
        default=mod.DefaultModsEnum.DEFAULT_MUZZLE, description="Muzzle modification"
    )
    magazine: Optional[mod.MagazineEnum] = Field(
        default=mod.DefaultModsEnum.DEFAULT_MAGAZINE,
        description="Magazine modification",
    )
    weapon_size: Optional[mod.WeaponSizeEnum] = Field(
        default=mod.DefaultModsEnum.DEFAULT_WEAPON_SIZE,
        description="Stock and barrel alterations",
    )
    ammo_size: mod.AmmoSizeEnum = Field(description="Ammo size of the gun")

    price: int = Field(..., ge=0, description="Weapon price in hunt dollars")
    has_ammo_B: bool = Field(
        default=False, description="Has alternative ammo type swappable im match"
    )

    @classmethod
    @field_validator("melee")
    def validate_melee(cls, v: str) -> mod.MeleeEnum:
        """Validate melee enum value"""
        try:
            # Convert string to enum to ensure it's valid
            return mod.MeleeEnum(v)
        except ValueError:
            valid_values = [e.value for e in mod.MeleeEnum]
            raise ValueError(f"Invalid input '{v}'. Must be one of {valid_values}")

    @classmethod
    @field_validator("sights")
    def validate_sights(cls, v: str) -> mod.SightsEnum:
        """Validate melee enum value"""
        try:
            # Convert string to enum to ensure it's valid
            return mod.SightsEnum(v)
        except ValueError:
            valid_values = [e.value for e in mod.SightsEnum]
            raise ValueError(f"Invalid input '{v}'. Must be one of {valid_values}")

    @classmethod
    @field_validator("muzzle")
    def validate_muzzle(cls, v: str) -> mod.MuzzleEnum:
        """Validate melee enum value"""
        try:
            # Convert string to enum to ensure it's valid
            return mod.MuzzleEnum(v)
        except ValueError:
            valid_values = [e.value for e in mod.MuzzleEnum]
            raise ValueError(f"Invalid input '{v}'. Must be one of {valid_values}")

    @classmethod
    @field_validator("magazine")
    def validate_magazine(cls, v: str) -> mod.MagazineEnum:
        """Validate melee enum value"""
        try:
            # Convert string to enum to ensure it's valid
            return mod.MagazineEnum(v)
        except ValueError:
            valid_values = [e.value for e in mod.MagazineEnum]
            raise ValueError(f"Invalid input '{v}'. Must be one of {valid_values}")

    @classmethod
    @field_validator("ammo_size")
    def validate_ammosize(cls, v: str) -> mod.AmmoSizeEnum:
        """Validate melee enum value"""
        try:
            # Convert string to enum to ensure it's valid
            return mod.AmmoSizeEnum(v)
        except ValueError:
            valid_values = [e.value for e in mod.AmmoSizeEnum]
            raise ValueError(f"Invalid input '{v}'. Must be one of {valid_values}")

    @classmethod
    @field_validator("ammo_size")
    def validate_weaponsize(cls, v: str) -> mod.AmmoSizeEnum:
        """Validate melee enum value"""
        try:
            # Convert string to enum to ensure it's valid
            return mod.AmmoSizeEnum(v)
        except ValueError:
            valid_values = [e.value for e in mod.WeaponSizeEnum]
            raise ValueError(f"Invalid input '{v}'. Must be one of {valid_values}")


class WeaponCreate(WeaponBase):
    sights: Optional[str] = mod.DefaultModsEnum.DEFAULT_SIGHTS
    melee: Optional[str] = mod.DefaultModsEnum.DEFAULT_MELEE
    muzzle: Optional[str] = mod.DefaultModsEnum.DEFAULT_MUZZLE
    magazine: Optional[str] = mod.DefaultModsEnum.DEFAULT_MAGAZINE
    weapon_size: Optional[str] = mod.DefaultModsEnum.DEFAULT_WEAPON_SIZE


class WeaponUpdate(BaseModel):
    name: Optional[str] = None
    weapon_type_id: Optional[int] = None
    core_gun_id: Optional[int] = None

    slot_size: Optional[int] = None
    sights: Optional[str] = mod.DefaultModsEnum.DEFAULT_SIGHTS
    melee: Optional[str] = mod.DefaultModsEnum.DEFAULT_MELEE
    muzzle: Optional[str] = mod.DefaultModsEnum.DEFAULT_MUZZLE
    magazine: Optional[str] = mod.DefaultModsEnum.DEFAULT_MAGAZINE
    weapon_size: Optional[str] = mod.DefaultModsEnum.DEFAULT_WEAPON_SIZE
    ammo_size: Optional[mod.AmmoSizeEnum] = Field(
        description="Ammo size of the gun", default=None
    )

    price: Optional[int] = None
    has_ammo_B: Optional[bool] = None


class WeaponResponse(WeaponBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
