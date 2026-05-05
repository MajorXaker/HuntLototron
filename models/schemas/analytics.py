from pydantic import BaseModel

from models.dto.teammate_stats import (
    MapStats,
    TeamCompositionStats,
    TeammateStats,
    WeaponStats,
)


class TeammateAnalytics(BaseModel):
    matches_total: int
    by_teammates: list[TeammateStats]
    by_team_compositions: list[TeamCompositionStats]


class WeaponAnalytics(BaseModel):
    matches_total: int
    by_weapons: list[WeaponStats]


class MapAnalytics(BaseModel):
    matches_total: int
    by_maps: list[MapStats]
