import sqlalchemy as sa

import models.db_models as m


class AmmoType(m.Model):
    __tablename__ = "ammo_types"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50), nullable=False)
