from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.infrastructure.database import get_db
from src.schemas import comments as schemas
from src.api.dependencies import get_current_user
from src.schemas import users as user_schemas
from src.domain.comments import CommentUseCase
from src.domain.likes import LikeUseCase
from src.core.exceptions.domain_exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)

router = APIRouter()


@router.get("/{comment_id}", response_model=schemas.CommentResponse)
async def get_comment(comment_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await CommentUseCase.get_by_id(db, comment_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "context": e.details},
        )


@router.put("/{comment_id}", response_model=schemas.CommentResponse)
async def update_comment(
    comment_id: int,
    comment_update: schemas.CommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: user_schemas.UserResponse = Depends(get_current_user),
):
    try:
        comment = await CommentUseCase.get_by_id(db, comment_id)
        if comment.author_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы не можете редактировать чужой комментарий",
            )
        return await CommentUseCase.update(db, comment_id, comment_update)
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


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: user_schemas.UserResponse = Depends(get_current_user),
):
    try:
        comment = await CommentUseCase.get_by_id(db, comment_id)
        if comment.author_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы не можете удалить чужой комментарий",
            )
        await CommentUseCase.delete(db, comment_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "context": e.details},
        )


@router.post("/{comment_id}/like", status_code=status.HTTP_200_OK)
async def toggle_comment_like(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await LikeUseCase.toggle_like(
        db=db, user_id=current_user.id, comment_id=comment_id
    )


@router.get("/{comment_id}/likes", response_model=List[user_schemas.UserResponse])
async def get_comment_likers(comment_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await LikeUseCase.get_comment_likers(db, comment_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
