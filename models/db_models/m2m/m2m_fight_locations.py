import sqlalchemy as sa

from models.db_models.base import Model


class M2MFightLocations(Model):
    __tablename__ = "m2m_fight_locations"

    match_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("matches.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    compound_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("compounds.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )

    fight_ordering = sa.Column(
        sa.Integer,
        nullable=False,
    )  # to understand which fights were won, and which were lost

    __table_args__ = (
        sa.PrimaryKeyConstraint(match_id, compound_id, name="unique_user_case"),
    )
