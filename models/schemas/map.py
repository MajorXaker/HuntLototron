from pydantic import BaseModel


class MapBase(BaseModel):
    name: str


class MapCreate(MapBase):
    pass


class MapResponse(MapBase):
    id: int
    name: str
