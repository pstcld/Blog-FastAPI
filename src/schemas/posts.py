from pydantic import Field, ConfigDict, field_validator
from datetime import datetime, timedelta, timezone
from typing import Optional
from .common import PublishedCreatedBase
from .users import UserResponse


class PostBase(PublishedCreatedBase):
    title: str = Field(..., max_length=256)
    text: str
    pub_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    location_id: Optional[int] = None
    category_id: Optional[int] = None

    @field_validator("pub_date")
    @classmethod
    def validate_pub_date(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value


class PostCreate(PostBase):
    author_id: Optional[int] = Field(default=None)
    image: Optional[str] = None

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, value: datetime) -> datetime:
        if value < datetime.now(timezone.utc) - timedelta(minutes=5):
            raise ValueError("Дата создания не может быть в прошлом")
        return value

    @field_validator("pub_date")
    @classmethod
    def validate_pub_date(cls, value: datetime) -> datetime:
        if value < datetime.now(timezone.utc) - timedelta(minutes=5):
            raise ValueError("Дата публикации не может быть в прошлом")
        return value

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "string",
                "text": "string",
                "is_published": True,
            }
        }
    )


class PostUpdate(PostBase):
    image: Optional[str] = None
    created_at: Optional[datetime] = None
    pub_date: Optional[datetime] = Field(default=None, exclude=True)

    @field_validator("pub_date")
    @classmethod
    def validate_pub_date_update(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return value
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        if value < datetime.now(timezone.utc) - timedelta(minutes=5):
            raise ValueError("Новая дата публикации не может быть в прошлом")
        return value

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "string",
                "text": "string",
                "is_published": True,
            }
        }
    )


class PostResponse(PostBase):
    id: int
    author_id: int
    author: UserResponse
    image: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
