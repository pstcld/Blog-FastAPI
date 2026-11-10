from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.infrastructure.database import get_db
from src.schemas import comments as schemas
from src.domain.comments import CommentUseCase
from src.core.exceptions.domain_exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)

router = APIRouter()


@router.get("/", response_model=List[schemas.CommentResponse])
def get_comments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return CommentUseCase.get_all(db, skip=skip, limit=limit)


@router.get("/{comment_id}", response_model=schemas.CommentResponse)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    try:
        return CommentUseCase.get_by_id(db, comment_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "context": e.details},
        )


@router.post(
    "/", response_model=schemas.CommentResponse, status_code=status.HTTP_201_CREATED
)
def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    try:
        return CommentUseCase.create(db, comment)
    except EntityAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.message, "context": e.details},
        )


@router.put("/{comment_id}", response_model=schemas.CommentResponse)
def update_comment(
    comment_id: int,
    comment_update: schemas.CommentUpdate,
    db: Session = Depends(get_db),
):
    try:
        return CommentUseCase.update(db, comment_id, comment_update)
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
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    try:
        CommentUseCase.delete(db, comment_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "context": e.details},
        )
