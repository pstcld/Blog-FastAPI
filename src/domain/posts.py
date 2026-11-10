from sqlalchemy.orm import Session
from src.schemas import posts as schemas
from src.infrastructure.repositories import PostRepository
from src.core.exceptions.database_exceptions import (
    RecordAlreadyExistsError,
    RecordNotFoundError,
)
from src.core.exceptions.domain_exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)


class PostUseCase:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return PostRepository.get_all(db, skip, limit)

    @staticmethod
    def get_by_id(db: Session, post_id: int):
        try:
            return PostRepository.get_by_id(db, post_id)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Публикация не найдена.",
                details={"action": "get_post", "post_id": post_id},
            )

    @staticmethod
    def create(db: Session, post: schemas.PostCreate):
        try:
            return PostRepository.create(db, post)
        except RecordAlreadyExistsError:
            raise EntityAlreadyExistsError(
                message="Не удалось создать публикацию.",
                details={"action": "create_post"},
            )

    @staticmethod
    def update(db: Session, post_id: int, post_update: schemas.PostUpdate):
        try:
            db_post = PostRepository.get_by_id(db, post_id)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Публикация для обновления не найдена.",
                details={"action": "update_post", "post_id": post_id},
            )

        try:
            return PostRepository.update(db, db_post, post_update)
        except RecordAlreadyExistsError:
            raise EntityAlreadyExistsError(
                message="Не удалось обновить публикацию.",
                details={"action": "update_post", "post_id": post_id},
            )

    @staticmethod
    def delete(db: Session, post_id: int):
        try:
            db_post = PostRepository.get_by_id(db, post_id)
            PostRepository.delete(db, db_post)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Публикация для удаления не найдена.",
                details={"action": "delete_post", "post_id": post_id},
            )
