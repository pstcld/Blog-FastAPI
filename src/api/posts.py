from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.schemas import posts as schemas
from src.infrastructure.database import get_db
from src.infrastructure.repositories import PostRepository

router = APIRouter()


@router.post(
    "/", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED
)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    return PostRepository.create(db=db, post=post)


@router.get("/", response_model=List[schemas.PostResponse])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return PostRepository.get_all(db, skip=skip, limit=limit)


@router.get("/{post_id}", response_model=schemas.PostResponse)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = PostRepository.get_by_id(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.put("/{post_id}", response_model=schemas.PostResponse)
def update_post(
    post_id: int, post_update: schemas.PostUpdate, db: Session = Depends(get_db)
):
    db_post = PostRepository.get_by_id(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostRepository.update(db, db_post, post_update)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    db_post = PostRepository.get_by_id(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    PostRepository.delete(db, db_post)
