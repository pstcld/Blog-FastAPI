from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.infrastructure import models
from src.schemas import categories as schemas
from src.infrastructure.database import get_db

router = APIRouter()


@router.post(
    "/", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED
)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get("/", response_model=List[schemas.CategoryResponse])
def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = db.query(models.Category).offset(skip).limit(limit).all()
    return categories


@router.put("/{category_id}", response_model=schemas.CategoryResponse)
def update_category(
    category_id: int, category: schemas.CategoryUpdate, db: Session = Depends(get_db)
):
    db_category = (
        db.query(models.Category).filter(models.Category.id == category_id).first()
    )
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    for key, value in category.model_dump().items():
        setattr(db_category, key, value)

    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_category = (
        db.query(models.Category).filter(models.Category.id == category_id).first()
    )
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(db_category)
    db.commit()
