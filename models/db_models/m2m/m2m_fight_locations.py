import sqlalchemy as sa

from models.db_models.base import Model, RecordTimestampFields


class M2MFightLocations(Model, RecordTimestampFields):
    __tablename__ = "m2m_fight_locations"

    match_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    compound_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("cases.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )

    __table_args__ = (
        sa.PrimaryKeyConstraint(match_id, compound_id, name="unique_user_case"),
    )
