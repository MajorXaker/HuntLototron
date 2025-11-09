from typing import Optional

from pydantic import BaseModel, model_validator

from models.enums.wl_status import WLStatusEnum
from datetime import date, timedelta


class MatchPlayerSchema(BaseModel):
    player_id: int

    slot_a_weapon_id: int
    slot_a_ammo_a_id: Optional[int] = None
    slot_a_ammo_b_id: Optional[int] = None
    slot_a_dual_wielding: bool = False

    slot_b_weapon_id: int
    slot_b_ammo_a_id: Optional[int] = None
    slot_b_ammo_b_id: Optional[int] = None
    slot_b_dual_wielding: bool = False

    kills: Optional[int] = None
    assists: Optional[int] = None
    deaths: Optional[int] = None
    bounty: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def check_card_number_not_present(cls, data):
        if not data["player_id"]:
            # empty pack == no row in database
            return None
        return data


class NewMatchSchema(BaseModel):
    date: Optional[date]

    player_1_id: int
    player_2_id: Optional[int]
    player_3_id: Optional[int]

    slot_a_weapon_id: int
    slot_a_ammo_a_id: Optional[int] = None
    slot_a_ammo_b_id: Optional[int] = None
    slot_a_dual_wielding: bool = False

    slot_b_weapon_id: int
    slot_b_ammo_a_id: Optional[int] = None
    slot_b_ammo_b_id: Optional[int] = None
    slot_b_dual_wielding: bool = False

class UpdateMatchSchema(BaseModel):
    """We could add here some fields that would indicate that the field got changed,
    so it's necessary to include its data to the query. However, there are no plans to distribute this system
    anymore. So the BE would be solely tied to a single and current FE.
    If by any chance this status quo changes - I'll be happy to rework the app to allow distribution
    and collaborative work"""

    date: date

    player_1_id: int
    player_2_id: Optional[int]
    player_3_id: Optional[int]

    slot_a_weapon_id: int
    slot_a_ammo_a_id: Optional[int] = None
    slot_a_ammo_b_id: Optional[int] = None
    slot_a_dual_wielding: bool = False

    slot_b_weapon_id: int
    slot_b_ammo_a_id: Optional[int] = None
    slot_b_ammo_b_id: Optional[int] = None
    slot_b_dual_wielding: bool = False

    wl_status: WLStatusEnum

    kills_total: int
    kills: int
    assists: int
    deaths: int
    bounty: int

    playtime: timedelta
    map_id: int
    fights_places_ids: list[int]

class FullMatchSchema(BaseModel):
    id: int
    wl_status: Optional[WLStatusEnum] = None
    date: Optional[date]
    kills_total: Optional[int] = None
    playtime: Optional[int] = (
        None  # timedelta returns weird result hard to work with - 'PT20M1S'
    )
    map_id: Optional[int] = None
    fights_places_ids: list[int]

    player_1_id: int
    player_2_id: Optional[int]
    player_3_id: Optional[int]

    player_1_data: MatchPlayerSchema
    player_2_data: Optional[MatchPlayerSchema]
    player_3_data: Optional[MatchPlayerSchema]

    fights_places_ids: Optional[list[int]]


class GetMatchesSchema(BaseModel):
    data: list[FullMatchSchema]
    total_results: int

class ShortMatchResponseSchema(BaseModel):
    match_id: int


class CreateMatchResultSchema(BaseModel):
    match_id: int

    wl_status: WLStatusEnum

    kills_total: int
    kills: int
    assists: int
    deaths: int
    bounty: int

    playtime: timedelta
    map_id: int
    fights_places_ids: list[int]
