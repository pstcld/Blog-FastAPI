from sqlalchemy.orm import Session
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
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return CategoryRepository.get_all(db, skip, limit)

    @staticmethod
    def get_by_id(db: Session, category_id: int):
        try:
            return CategoryRepository.get_by_id(db, category_id)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Категория не найдена.",
                details={"action": "get_category", "category_id": category_id},
            )

    @staticmethod
    def create(db: Session, category: schemas.CategoryCreate):
        try:
            return CategoryRepository.create(db, category)
        except RecordAlreadyExistsError:
            raise EntityAlreadyExistsError(
                message="Не удалось создать категорию: такой slug уже существует.",
                details={"action": "create_category", "slug": category.slug},
            )

    @staticmethod
    def update(db: Session, category_id: int, category_update: schemas.CategoryUpdate):
        try:
            db_category = CategoryRepository.get_by_id(db, category_id)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Категория для обновления не найдена.",
                details={"action": "update_category", "category_id": category_id},
            )

        try:
            return CategoryRepository.update(db, db_category, category_update)
        except RecordAlreadyExistsError:
            raise EntityAlreadyExistsError(
                message="Не удалось обновить категорию: slug уже занят.",
                details={"action": "update_category", "category_id": category_id},
            )

    @staticmethod
    def delete(db: Session, category_id: int):
        try:
            db_category = CategoryRepository.get_by_id(db, category_id)
            CategoryRepository.delete(db, db_category)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Категория для удаления не найдена.",
                details={"action": "delete_category", "category_id": category_id},
            )
