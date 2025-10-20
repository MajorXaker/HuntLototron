from typing import Optional

from pydantic import BaseModel, ConfigDict


class AmmoTypeBase(BaseModel):
    name: str


class AmmoTypeCreate(AmmoTypeBase):
    pass


class AmmoTypeUpdate(BaseModel):
    name: Optional[str] = None


class AmmoTypeResponse(AmmoTypeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
