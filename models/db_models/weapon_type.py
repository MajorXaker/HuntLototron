import sqlalchemy as sa

from .base import Model


class WeaponType(Model):
    __tablename__ = "weapon_types"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(255), nullable=False, unique=True)
