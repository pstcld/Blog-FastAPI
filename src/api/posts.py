from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.infrastructure.database import get_db
from src.schemas import posts as schemas
from src.api.dependencies import get_current_user
from src.schemas import users as user_schemas
from src.domain.posts import PostUseCase
from fastapi.responses import FileResponse
import os
from src.core.exceptions.domain_exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)

router = APIRouter()


@router.get("/", response_model=List[schemas.PostResponse])
def get_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return PostUseCase.get_all(db, skip=skip, limit=limit)


@router.get("/{post_id}", response_model=schemas.PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    try:
        return PostUseCase.get_by_id(db, post_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "context": e.details},
        )


@router.post(
    "/", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED
)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserResponse = Depends(get_current_user),
):
    try:
        post.author_id = current_user.id
        return PostUseCase.create(db, post)
    except EntityAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.message, "context": e.details},
        )


@router.put("/{post_id}", response_model=schemas.PostResponse)
def update_post(
    post_id: int,
    post_update: schemas.PostUpdate,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserResponse = Depends(get_current_user),
):
    try:
        post = PostUseCase.get_by_id(db, post_id)
        if post.author_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас нет прав на редактирование чужого поста",
            )
        return PostUseCase.update(db, post_id, post_update)
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
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserResponse = Depends(get_current_user),
):
    try:
        post = PostUseCase.get_by_id(db, post_id)
        if post.author_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас нет прав на удаление чужого поста",
            )
        PostUseCase.delete(db, post_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "context": e.details},
        )


@router.post("/{post_id}/image", response_model=schemas.PostResponse)
def upload_post_image(
    post_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return PostUseCase.upload_image(
        db=db, post_id=post_id, file=file, current_user_id=current_user.id
    )


@router.get("/{post_id}/image", response_class=FileResponse)
def get_post_image_by_id(post_id: int, db: Session = Depends(get_db)):
    try:
        post = PostUseCase.get_by_id(db, post_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail="Пост не найден")
    if not post.image:
        raise HTTPException(status_code=404, detail="У этого поста нет изображения")
    file_path = post.image.lstrip("/")
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404, detail="Изображение отсутствует на сервере"
        )
    return FileResponse(path=file_path)
