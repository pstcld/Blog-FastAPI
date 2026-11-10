from pydantic import Field, field_validator
from typing import Optional
from src.schemas.common import PublishedCreatedBase, BaseResponse


class CategoryBase(PublishedCreatedBase):
    title: str = Field(..., max_length=250)
    description: Optional[str] = None
    slug: str = Field(..., max_length=100)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Название категории не может быть пустым")
        return cleaned

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        if " " in value:
            raise ValueError("Slug не должен содержать пробелов")
        if not value.islower():
            raise ValueError("Slug должен состоять только из строчных букв")
        return value


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class CategoryResponse(CategoryBase, BaseResponse):
    pass
