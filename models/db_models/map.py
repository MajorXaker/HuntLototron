import sqlalchemy as sa

from .base import Model


class Map(Model):
    __tablename__ = "maps"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(80))
