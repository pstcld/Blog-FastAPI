from pydantic import Field
from .common import PublishedCreatedBase


class LocationBase(PublishedCreatedBase):
    name: str = Field(..., max_length=256)


class LocationCreate(LocationBase):
    pass


class LocationUpdate(LocationBase):
    pass


class LocationResponse(LocationBase):
    id: int

    class Config:
        from_attributes = True
