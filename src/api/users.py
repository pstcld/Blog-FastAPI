from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.infrastructure.database import get_db
from src.api.dependencies import get_current_user
from src.schemas import users as schemas
from src.schemas import posts as post_schemas
from src.domain.users import UserUseCase
from src.domain.posts import PostUseCase
from src.domain.likes import LikeUseCase
from src.core.security import create_access_token
from src.core.exceptions.domain_exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)

router = APIRouter()


@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_profile(
    current_user: schemas.UserResponse = Depends(get_current_user),
):
    return current_user


@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await UserUseCase.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/", response_model=List[schemas.UserResponse])
async def get_users(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    return await UserUseCase.get_all(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await UserUseCase.get_by_id(db, user_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "context": e.details},
        )


@router.post(
    "/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await UserUseCase.create(db, user)
    except EntityAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.message, "context": e.details},
        )


@router.get("/{user_id}/posts", response_model=List[post_schemas.PostResponse])
async def get_user_posts(
    user_id: int, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    try:
        return await PostUseCase.get_by_author_id(
            db, author_id=user_id, skip=skip, limit=limit
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{user_id}/likes/posts", response_model=List[post_schemas.PostResponse])
async def get_user_liked_posts(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await LikeUseCase.get_user_liked_posts(db, user_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
