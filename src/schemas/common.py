from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone


class PublishedCreatedBase(BaseModel):
    is_published: bool = True
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))


class BaseResponse(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)
