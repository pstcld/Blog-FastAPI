from sqlalchemy.orm import Session
from src.schemas import locations as schemas
from src.infrastructure.repositories import LocationRepository
from src.core.exceptions.database_exceptions import (
    RecordAlreadyExistsError,
    RecordNotFoundError,
)
from src.core.exceptions.domain_exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)


class LocationUseCase:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return LocationRepository.get_all(db, skip, limit)

    @staticmethod
    def get_by_id(db: Session, location_id: int):
        try:
            return LocationRepository.get_by_id(db, location_id)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Локация не найдена.",
                details={"action": "get_location", "location_id": location_id},
            )

    @staticmethod
    def create(db: Session, location: schemas.LocationCreate):
        try:
            return LocationRepository.create(db, location)
        except RecordAlreadyExistsError:
            raise EntityAlreadyExistsError(
                message="Не удалось добавить локацию: конфликт уникальных данных.",
                details={"action": "create_location", "name": location.name},
            )

    @staticmethod
    def update(db: Session, location_id: int, location_update: schemas.LocationUpdate):
        try:
            db_location = LocationRepository.get_by_id(db, location_id)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Локация для обновления не найдена.",
                details={"action": "update_location", "location_id": location_id},
            )

        try:
            return LocationRepository.update(db, db_location, location_update)
        except RecordAlreadyExistsError:
            raise EntityAlreadyExistsError(
                message="Не удалось обновить локацию: конфликт уникальных данных.",
                details={"action": "update_location", "location_id": location_id},
            )

    @staticmethod
    def delete(db: Session, location_id: int):
        try:
            db_location = LocationRepository.get_by_id(db, location_id)
            LocationRepository.delete(db, db_location)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Локация для удаления не найдена.",
                details={"action": "delete_location", "location_id": location_id},
            )
