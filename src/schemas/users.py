from pydantic import BaseModel, EmailStr, Field, field_validator
from src.schemas.common import BaseResponse


class UserBase(BaseModel):
    username: str = Field(..., max_length=150)
    email: EmailStr = Field(..., max_length=255)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if " " in value:
            raise ValueError("Имя пользователя не должно содержать пробелов")
        if len(value) < 3:
            raise ValueError("Имя пользователя должно быть не короче 3 символов")
        return value


class UserCreate(UserBase):
    password: str = Field(..., min_length=4)


class UserCreateDB(UserBase):
    hashed_password: str


class UserResponse(UserBase, BaseResponse):
    is_admin: bool


class Token(BaseModel):
    access_token: str
    token_type: str
