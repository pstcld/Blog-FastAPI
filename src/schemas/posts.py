from pydantic import Field
from datetime import datetime
from typing import Optional
from .common import PublishedCreatedBase
from .users import UserResponse


class PostBase(PublishedCreatedBase):
    title: str = Field(..., max_length=256)
    text: str
    pub_date: datetime
    location_id: Optional[int] = None
    category_id: Optional[int] = None


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

    class Config:
        from_attributes = True
