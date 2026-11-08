from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.schemas import categories as schemas
from src.infrastructure.database import get_db
from src.infrastructure.repositories import CategoryRepository

router = APIRouter()


@router.post(
    "/", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED
)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    return CategoryRepository.create(db=db, category=category)


@router.get("/", response_model=List[schemas.CategoryResponse])
def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return CategoryRepository.get_all(db, skip=skip, limit=limit)


@router.put("/{category_id}", response_model=schemas.CategoryResponse)
def update_category(
    category_id: int, category: schemas.CategoryUpdate, db: Session = Depends(get_db)
):
    db_category = CategoryRepository.get_by_id(db, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryRepository.update(db, db_category, category)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_category = CategoryRepository.get_by_id(db, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    CategoryRepository.delete(db, db_category)
