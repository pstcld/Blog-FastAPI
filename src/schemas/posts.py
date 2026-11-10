from pydantic import Field, ConfigDict, field_validator
from datetime import datetime, timedelta, timezone
from typing import Optional
from .common import PublishedCreatedBase
from .users import UserResponse


class PostBase(PublishedCreatedBase):
    title: str = Field(..., max_length=256)
    text: str
    pub_date: datetime
    location_id: Optional[int] = None
    category_id: Optional[int] = None

    @field_validator("pub_date")
    @classmethod
    def validate_pub_date(cls, value: datetime) -> datetime:
        if value < datetime.now(timezone.utc) - timedelta(minutes=5):
            raise ValueError("Дата публикации не может быть в прошлом")
        return value


class PostCreate(PostBase):
    author_id: int
    image: Optional[str] = None


class PostUpdate(PostBase):
    image: Optional[str] = None


class PostResponse(PostBase):
    id: int
    author_id: int
    author: UserResponse
    image: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
