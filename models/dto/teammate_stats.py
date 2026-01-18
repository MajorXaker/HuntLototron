from datetime import date
from typing import Optional

from pydantic import BaseModel


class BaseMatchStats(BaseModel):
    wins: int
    losses: int
    flees: int
    winrate: float
    match_share: float
    total_matches: int
    first_match: date
    last_match: date
    median_playtime_seconds: float


class TeammateStats(BaseMatchStats):
    teammate_id: int
    teammate_name: str


class TeamCompositionStats(BaseMatchStats):
    teammate_a_id: int
    teammate_a_name: str
    teammate_b_id: Optional[int]
    teammate_b_name: Optional[str]
