from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from src.api.dependencies import get_current_user
from src.infrastructure.database import get_db
from src.schemas import posts as schemas
from src.schemas import users as user_schemas
from src.schemas import comments as comment_schemas
from src.domain.posts import PostUseCase
from src.domain.comments import CommentUseCase
from src.domain.likes import LikeUseCase
from fastapi.responses import FileResponse
import os
from src.core.exceptions.domain_exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)

router = APIRouter()


@router.get("/", response_model=list[schemas.PostResponse])
async def get_posts(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    location_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    return await PostUseCase.get_all(
        db, skip=skip, limit=limit, category_id=category_id, location_id=location_id
    )


@router.get("/{post_id}", response_model=schemas.PostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await PostUseCase.get_by_id(db, post_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "context": e.details},
        )


@router.post(
    "/", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED
)
async def create_post(
    post: schemas.PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: user_schemas.UserResponse = Depends(get_current_user),
):
    try:
        post.author_id = current_user.id
        return await PostUseCase.create(db, post)
    except EntityAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.message, "context": e.details},
        )


@router.put("/{post_id}", response_model=schemas.PostResponse)
async def update_post(
    post_id: int,
    post_update: schemas.PostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: user_schemas.UserResponse = Depends(get_current_user),
):
    try:
        post = await PostUseCase.get_by_id(db, post_id)
        if post.author_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас нет прав на редактирование чужого поста",
            )
        return await PostUseCase.update(db, post_id, post_update)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "context": e.details},
        )
    except EntityAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.message, "context": e.details},
        )


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: user_schemas.UserResponse = Depends(get_current_user),
):
    try:
        post = await PostUseCase.get_by_id(db, post_id)
        if post.author_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас нет прав на удаление чужого поста",
            )
        await PostUseCase.delete(db, post_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "context": e.details},
        )


@router.post("/{post_id}/image", response_model=schemas.PostResponse)
async def upload_post_image(
    post_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: user_schemas.UserResponse = Depends(get_current_user),
):
    try:
        post = await PostUseCase.get_by_id(db, post_id)
        if post.author_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет прав на изменение этого поста",
            )
        return await PostUseCase.upload_image(db, post_id, file)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "context": getattr(e, "details", {})},
        )


@router.get("/{post_id}/image", response_class=FileResponse)
async def get_post_image_by_id(post_id: int, db: AsyncSession = Depends(get_db)):
    try:
        post = await PostUseCase.get_by_id(db, post_id)
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Пост не найден")
    if not post.image:
        raise HTTPException(status_code=404, detail="У этого поста нет изображения")
    file_path = post.image.lstrip("/")
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404, detail="Изображение отсутствует на сервере"
        )
    return FileResponse(path=file_path)


@router.delete("/{post_id}/image", response_model=schemas.PostResponse)
async def delete_post_image(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: user_schemas.UserResponse = Depends(get_current_user),
):
    post = await PostUseCase.get_by_id(db, post_id)
    if post.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403, detail="Недостаточно прав для удаления изображения"
        )

    return await PostUseCase.delete_image(db, post_id)


@router.get(
    "/{post_id}/comments/", response_model=List[comment_schemas.CommentResponse]
)
async def get_post_comments(
    post_id: int, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    try:
        await PostUseCase.get_by_id(db, post_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "context": e.details},
        )

    return await CommentUseCase.get_by_post_id(db, post_id, skip=skip, limit=limit)


@router.post(
    "/{post_id}/comments/",
    response_model=comment_schemas.CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post_comment(
    post_id: int,
    comment: comment_schemas.CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: user_schemas.UserResponse = Depends(get_current_user),
):
    try:
        await PostUseCase.get_by_id(db, post_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "context": e.details},
        )

    comment.author_id = current_user.id
    comment.post_id = post_id

    try:
        return await CommentUseCase.create(db, comment)
    except EntityAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.message, "context": e.details},
        )


@router.post("/{post_id}/like", status_code=status.HTTP_200_OK)
async def toggle_post_like(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await LikeUseCase.toggle_like(
        db=db, user_id=current_user.id, post_id=post_id
    )


@router.get("/{post_id}/likes", response_model=List[user_schemas.UserResponse])
async def get_post_likers(post_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await LikeUseCase.get_post_likers(db, post_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
