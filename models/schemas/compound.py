from typing import Optional

from pydantic import BaseModel, ConfigDict


class CompoundBase(BaseModel):
    name: str
    map_id: int
    double_clue: bool
    # x_relative: float = -2.0
    # y_relative: float = -2.0


class CompoundCreate(CompoundBase):
    pass


class CompoundUpdate(BaseModel):
    map_id: Optional[int] = None
    double_clue: Optional[bool] = None
    # x_relative: Optional[float] = None
    # y_relative: Optional[float] = None


class CompoundResponse(CompoundBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
