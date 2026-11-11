from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas import categories as schemas
from src.infrastructure.repositories import CategoryRepository
from src.core.exceptions.database_exceptions import (
    RecordAlreadyExistsError,
    RecordNotFoundError,
)
from src.core.exceptions.domain_exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)


class CategoryUseCase:
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100):
        return await CategoryRepository.get_all(db, skip, limit)

    @staticmethod
    async def get_by_id(db: AsyncSession, category_id: int):
        try:
            return await CategoryRepository.get_by_id(db, category_id)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Категория не найдена.",
                details={"action": "get_category", "category_id": category_id},
            )

    @staticmethod
    async def create(db: AsyncSession, category: schemas.CategoryCreate):
        try:
            return await CategoryRepository.create(db, category)
        except RecordAlreadyExistsError:
            raise EntityAlreadyExistsError(
                message="Не удалось создать категорию: такой slug уже существует.",
                details={"action": "create_category", "slug": category.slug},
            )

    @staticmethod
    async def update(
        db: AsyncSession, category_id: int, category_update: schemas.CategoryUpdate
    ):
        try:
            db_category = await CategoryRepository.get_by_id(db, category_id)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Категория для обновления не найдена.",
                details={"action": "update_category", "category_id": category_id},
            )

        try:
            return await CategoryRepository.update(db, db_category, category_update)
        except RecordAlreadyExistsError:
            raise EntityAlreadyExistsError(
                message="Не удалось обновить категорию: slug уже занят.",
                details={"action": "update_category", "category_id": category_id},
            )

    @staticmethod
    async def delete(db: AsyncSession, category_id: int):
        try:
            db_category = await CategoryRepository.get_by_id(db, category_id)
            await CategoryRepository.delete(db, db_category)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Категория для удаления не найдена.",
                details={"action": "delete_category", "category_id": category_id},
            )
