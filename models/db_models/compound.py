import sqlalchemy as sa

import models.db_models as m


class Compound(m.Model):
    __tablename__ = "compounds"

    name = sa.Column(sa.String(80), primary_key=True)
    map_id = sa.Column(sa.ForeignKey(m.Map.id, ondelete="RESTRICT"), nullable=False)
    double_clue = sa.Column(sa.Boolean, nullable=False)

    # TODO probably delete
    x_relative = sa.Column(sa.Float, nullable=False, default=-2)
    y_relative = sa.Column(sa.Float, nullable=False, default=-2)
