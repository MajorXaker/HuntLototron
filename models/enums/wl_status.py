from enum import StrEnum


class WLStatusEnum(StrEnum):
    WIN = "win"
    LOSE = "lose"
    FLEE = "flee"  # extract without bounty
