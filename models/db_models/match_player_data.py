import sqlalchemy as sa

import models.db_models as m


class MatchPlayerData(m.Model):
    __tablename__ = "match_player_data"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    player_id = sa.Column(
        sa.ForeignKey(m.Player.id, ondelete="RESTRICT"), nullable=False
    )

    slot_a_weapon_id = sa.Column(
        sa.ForeignKey(m.Weapon.id, ondelete="RESTRICT"), nullable=True
    )
    slot_a_ammo_a_id = sa.Column(
        sa.ForeignKey(m.AmmoType.id, ondelete="RESTRICT"), nullable=True
    )
    slot_a_ammo_b_id = sa.Column(
        sa.ForeignKey(m.AmmoType.id, ondelete="RESTRICT"), nullable=True
    )
    slot_a_dual_wielding = sa.Column(sa.Boolean, nullable=False, default=False)

    slot_b_weapon_id = sa.Column(
        sa.ForeignKey(m.Weapon.id, ondelete="RESTRICT"), nullable=True
    )
    slot_b_ammo_a_id = sa.Column(
        sa.ForeignKey(m.AmmoType.id, ondelete="RESTRICT"), nullable=True
    )
    slot_b_ammo_b_id = sa.Column(
        sa.ForeignKey(m.AmmoType.id, ondelete="RESTRICT"), nullable=True
    )
    slot_b_dual_wielding = sa.Column(sa.Boolean, nullable=False, default=False)

    kills = sa.Column(sa.Integer, nullable=False, default=0)
    assists = sa.Column(sa.Integer, nullable=False, default=0)
    deaths = sa.Column(sa.Integer, nullable=False, default=0)
    bounty = sa.Column(sa.Integer, nullable=False, default=0)
