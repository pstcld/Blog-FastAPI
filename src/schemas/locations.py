from pydantic import Field, field_validator
from src.schemas.common import PublishedCreatedBase, BaseResponse


class LocationBase(PublishedCreatedBase):
    name: str = Field(..., max_length=250)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Название локации не может быть пустым")
        return cleaned


class LocationCreate(LocationBase):
    pass


class LocationUpdate(LocationBase):
    pass


class LocationResponse(LocationBase, BaseResponse):
    pass
