from typing import Optional

from pydantic import BaseModel, ConfigDict


class PlayerBase(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None


class PlayerCreate(PlayerBase):
    pass


class PlayerUpdate(BaseModel):
    username: Optional[str] = None
    is_disabled: Optional[bool] = None


class PlayerResponse(PlayerBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
