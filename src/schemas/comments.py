from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
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
    author_id: int
    post_id: int


class CommentUpdate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: int
    created_at: datetime
    author_id: int
    post_id: int
    author: UserResponse

    model_config = ConfigDict(from_attributes=True)
