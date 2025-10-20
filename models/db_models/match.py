from datetime import date

import sqlalchemy as sa

import models.db_models as m


# # Association table for many-to-many relationship
# match_compounds = sa.Table(
#     "match_compounds",
#     Model.metadata,
#     sa.Column("match_id", sa.ForeignKey("matches.id", ondelete="CASCADE")),
#     sa.Column("compound_name", sa.ForeignKey("compounds.name", ondelete="RESTRICT")),
# )
#


class Match(m.Model):
    __tablename__ = "matches"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    wl_status = sa.Column(sa.Float, nullable=False, default=0)
    date = sa.Column(sa.Date, nullable=False, default=date.today)
    kills_total = sa.Column(sa.Integer, nullable=False, default=0)
    playtime = sa.Column(sa.Interval, nullable=False)
    map_name = sa.Column(sa.ForeignKey(m.Map.id, ondelete="RESTRICT"), nullable=True)

    # Player 1 fields
    player_1_id = sa.Column(
        sa.ForeignKey(m.Player.id, ondelete="RESTRICT"), nullable=False
    )
    player_1_match_data = sa.Column(
        sa.ForeignKey(m.MatchPlayerData.id, ondelete="RESTRICT"), nullable=False
    )

    # Player 2 fields
    player_2_id = sa.Column(
        sa.ForeignKey(m.Player.id, ondelete="RESTRICT"), nullable=True
    )
    player_2_match_data = sa.Column(
        sa.ForeignKey(m.MatchPlayerData.id, ondelete="RESTRICT"), nullable=False
    )

    # Player 2 fields
    player_3_id = sa.Column(
        sa.ForeignKey(m.Player.id, ondelete="RESTRICT"), nullable=True
    )
    player_3_match_data = sa.Column(
        sa.ForeignKey(m.MatchPlayerData.id, ondelete="RESTRICT"), nullable=False
    )
