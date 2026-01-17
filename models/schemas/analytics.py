from pydantic import BaseModel

from models.dto.teammate_stats import TeamCompositionStats, TeammateStats


class TeammateAnalytics(BaseModel):
    matches_total: int
    by_teammates: list[TeammateStats]
    by_team_compositions: list[TeamCompositionStats]
