from typing import Optional

from pydantic import BaseModel, ConfigDict


class WeaponTypeBase(BaseModel):
    name: str


class WeaponTypeCreate(WeaponTypeBase):
    pass


class WeaponTypeUpdate(BaseModel):
    name: Optional[str] = None


class WeaponTypeResponse(WeaponTypeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
