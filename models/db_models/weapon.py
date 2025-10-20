import sqlalchemy as sa

import models.db_models as m
import models.enums.weapon_modifiers as mod


class Weapon(m.Model):
    __tablename__ = "weapons"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50), nullable=False, unique=True)
    weapon_type_id = sa.Column(
        sa.ForeignKey(m.WeaponType.id, ondelete="RESTRICT"), nullable=False
    )
    core_gun_id = sa.Column(
        sa.ForeignKey("weapons.id", ondelete="RESTRICT"), nullable=True
    )

    size = sa.Column(sa.Integer, nullable=False)

    sights: mod.SightsEnum = sa.Column(sa.String(50), nullable=False)
    melee: mod.MeleeEnum = sa.Column(sa.String(50), nullable=False)
    muzzle: mod.MuzzleEnum = sa.Column(sa.String(50), nullable=False)
    magazine: mod.MagazineEnum = sa.Column(sa.String(50), nullable=False)
    ammo_size: mod.AmmoSizeEnum = sa.Column(sa.String(50), nullable=False)

    price = sa.Column(sa.Integer, nullable=False)
    has_ammo_B = sa.Column(
        sa.Boolean,
        nullable=False,
        default=False,
        doc="If the weapon able to use 2 different ammo at once",
    )
