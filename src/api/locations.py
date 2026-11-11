from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.infrastructure.database import get_db
from src.schemas import locations as schemas
from src.api.dependencies import get_current_admin_user, get_current_user
from src.schemas import users as user_schemas
from src.domain.locations import LocationUseCase
from src.core.exceptions.domain_exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)

router = APIRouter()


@router.get("/", response_model=List[schemas.LocationResponse])
async def get_locations(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    return await LocationUseCase.get_all(db, skip=skip, limit=limit)


@router.get("/{location_id}", response_model=schemas.LocationResponse)
async def get_location(location_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await LocationUseCase.get_by_id(db, location_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "context": e.details},
        )


@router.post(
    "/", response_model=schemas.LocationResponse, status_code=status.HTTP_201_CREATED
)
async def create_location(
    location: schemas.LocationCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: user_schemas.UserResponse = Depends(get_current_user),
):
    try:
        return await LocationUseCase.create(db, location)
    except EntityAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.message, "context": e.details},
        )


@router.put("/{location_id}", response_model=schemas.LocationResponse)
async def update_location(
    location_id: int,
    location_update: schemas.LocationUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: user_schemas.UserResponse = Depends(get_current_admin_user),
):
    try:
        return await LocationUseCase.update(db, location_id, location_update)
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


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: user_schemas.UserResponse = Depends(get_current_admin_user),
):
    try:
        await LocationUseCase.delete(db, location_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "context": e.details},
        )
