import sqlalchemy as sa
from sqlalchemy import UniqueConstraint

import models.db_models as m


class Compound(m.Model):
    __tablename__ = "compounds"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(80))
    map_id = sa.Column(sa.ForeignKey(m.Map.id, ondelete="RESTRICT"), nullable=False)
    double_clue = sa.Column(sa.Boolean, nullable=False)

    # TODO probably delete
    x_relative = sa.Column(sa.Float, nullable=False, default=-2)
    y_relative = sa.Column(sa.Float, nullable=False, default=-2)

    __table_args__ = (UniqueConstraint(map_id, name, name="unique_compound_per_map"),)
