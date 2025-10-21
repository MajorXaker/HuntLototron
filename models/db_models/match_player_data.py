import sqlalchemy as sa

import models.db_models as m


class MatchPlayerData(m.Model):
    __tablename__ = "match_player_data"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    player_id = sa.Column(
        sa.ForeignKey(m.Player.id, ondelete="RESTRICT"), nullable=False
    )

    primary_weapon_id = sa.Column(
        sa.ForeignKey(m.Weapon.id, ondelete="RESTRICT"), nullable=True
    )
    primary_ammo_A_id = sa.Column(
        sa.ForeignKey(m.AmmoType.id, ondelete="RESTRICT"), nullable=True
    )
    primary_ammo_B_id = sa.Column(
        sa.ForeignKey(m.AmmoType.id, ondelete="RESTRICT"), nullable=True
    )

    secondary_weapon_id = sa.Column(
        sa.ForeignKey(m.Weapon.id, ondelete="RESTRICT"), nullable=True
    )
    secondary_ammo_A_id = sa.Column(
        sa.ForeignKey(m.AmmoType.id, ondelete="RESTRICT"), nullable=True
    )
    secondary_ammo_B_id = sa.Column(
        sa.ForeignKey(m.AmmoType.id, ondelete="RESTRICT"), nullable=True
    )

    kills = sa.Column(sa.Integer, nullable=False, default=0)
    assists = sa.Column(sa.Integer, nullable=False, default=0)
    deaths = sa.Column(sa.Integer, nullable=False, default=0)
    bounty = sa.Column(sa.Integer, nullable=False, default=0)
