import sqlalchemy as sa

import models.db_models as m
from models.enums.player_status import PlayerStatusEnum


class Player(m.Model):
    __tablename__ = "players"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    username = sa.Column(sa.String(50), nullable=False)

    status: PlayerStatusEnum = sa.Column(
        sa.String,
        nullable=False,
        default=PlayerStatusEnum.ACTIVE,
        server_default=PlayerStatusEnum.ACTIVE,
    )
