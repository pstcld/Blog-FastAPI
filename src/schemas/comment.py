from pydantic import BaseModel
from datetime import datetime
from .user import UserResponse


class CommentBase(BaseModel):
    text: str


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

    class Config:
        from_attributes = True
