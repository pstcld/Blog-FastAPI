from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.schemas import comments as schemas
from src.infrastructure.database import get_db
from src.infrastructure.repositories import CommentRepository

router = APIRouter()


@router.post(
    "/", response_model=schemas.CommentResponse, status_code=status.HTTP_201_CREATED
)
def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    return CommentRepository.create(db=db, comment=comment)


@router.get("/", response_model=List[schemas.CommentResponse])
def get_comments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return CommentRepository.get_all(db, skip=skip, limit=limit)


@router.put("/{comment_id}", response_model=schemas.CommentResponse)
def update_comment(
    comment_id: int, comment: schemas.CommentUpdate, db: Session = Depends(get_db)
):
    db_comment = CommentRepository.get_by_id(db, comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return CommentRepository.update(db, db_comment, comment)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    db_comment = CommentRepository.get_by_id(db, comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    CommentRepository.delete(db, db_comment)
