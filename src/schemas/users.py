from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(..., max_length=150)


class UserCreate(UserBase):
    password: str = Field(..., min_length=4)


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True
