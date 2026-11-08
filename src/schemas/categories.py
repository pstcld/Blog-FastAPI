from pydantic import Field
from .common import PublishedCreatedBase


class CategoryBase(PublishedCreatedBase):
    title: str = Field(..., max_length=256)
    description: str
    slug: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True
