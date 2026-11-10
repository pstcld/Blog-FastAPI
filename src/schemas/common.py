from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime, timezone


class PublishedCreatedBase(BaseModel):
    is_published: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value


class BaseResponse(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)
