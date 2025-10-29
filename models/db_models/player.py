import sqlalchemy as sa

import models.db_models as m


class Player(m.Model):
    __tablename__ = "players"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    username = sa.Column(sa.String(50), nullable=False)
