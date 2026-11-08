from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.schemas import locations as schemas
from src.infrastructure.database import get_db
from src.infrastructure.repositories import LocationRepository

router = APIRouter()


@router.post(
    "/", response_model=schemas.LocationResponse, status_code=status.HTTP_201_CREATED
)
def create_location(location: schemas.LocationCreate, db: Session = Depends(get_db)):
    return LocationRepository.create(db=db, location=location)


@router.get("/", response_model=List[schemas.LocationResponse])
def get_locations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return LocationRepository.get_all(db, skip=skip, limit=limit)


@router.put("/{location_id}", response_model=schemas.LocationResponse)
def update_location(
    location_id: int, location: schemas.LocationUpdate, db: Session = Depends(get_db)
):
    db_location = LocationRepository.get_by_id(db, location_id)
    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")
    return LocationRepository.update(db, db_location, location)


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(location_id: int, db: Session = Depends(get_db)):
    db_location = LocationRepository.get_by_id(db, location_id)
    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")
    LocationRepository.delete(db, db_location)
