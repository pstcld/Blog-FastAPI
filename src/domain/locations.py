from sqlalchemy.ext.asyncio import AsyncSession
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
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100):
        return await LocationRepository.get_all(db, skip, limit)

    @staticmethod
    async def get_by_id(db: AsyncSession, location_id: int):
        try:
            return await LocationRepository.get_by_id(db, location_id)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Локация не найдена.",
                details={"action": "get_location", "location_id": location_id},
            )

    @staticmethod
    async def create(db: AsyncSession, location: schemas.LocationCreate):
        try:
            return await LocationRepository.create(db, location)
        except RecordAlreadyExistsError:
            raise EntityAlreadyExistsError(
                message="Не удалось добавить локацию: конфликт уникальных данных.",
                details={"action": "create_location", "name": location.name},
            )

    @staticmethod
    async def update(
        db: AsyncSession, location_id: int, location_update: schemas.LocationUpdate
    ):
        try:
            db_location = await LocationRepository.get_by_id(db, location_id)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Локация для обновления не найдена.",
                details={"action": "update_location", "location_id": location_id},
            )

        try:
            return await LocationRepository.update(db, db_location, location_update)
        except RecordAlreadyExistsError:
            raise EntityAlreadyExistsError(
                message="Не удалось обновить локацию: конфликт уникальных данных.",
                details={"action": "update_location", "location_id": location_id},
            )

    @staticmethod
    async def delete(db: AsyncSession, location_id: int):
        try:
            db_location = await LocationRepository.get_by_id(db, location_id)
            await LocationRepository.delete(db, db_location)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Локация для удаления не найдена.",
                details={"action": "delete_location", "location_id": location_id},
            )
