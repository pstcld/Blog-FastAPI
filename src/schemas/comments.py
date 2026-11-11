from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Optional
from .users import UserResponse


class CommentBase(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Комментарий не может быть пустым")
        return cleaned


class CommentCreate(CommentBase):
    author_id: Optional[int] = Field(default=None, exclude=True)
    post_id: Optional[int] = Field(default=None, exclude=True)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "string",
            }
        }
    )


class CommentUpdate(CommentBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "string",
            }
        }
    )


class CommentResponse(CommentBase):
    id: int
    created_at: datetime
    author_id: int
    post_id: int
    author: UserResponse

    model_config = ConfigDict(from_attributes=True)
