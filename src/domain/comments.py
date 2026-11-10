from sqlalchemy.orm import Session
from src.schemas import comments as schemas
from src.infrastructure.repositories import CommentRepository
from src.core.exceptions.database_exceptions import (
    RecordAlreadyExistsError,
    RecordNotFoundError,
)
from src.core.exceptions.domain_exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)


class CommentUseCase:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return CommentRepository.get_all(db, skip, limit)

    @staticmethod
    def get_by_id(db: Session, comment_id: int):
        try:
            return CommentRepository.get_by_id(db, comment_id)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Комментарий не найден.",
                details={"action": "get_comment", "comment_id": comment_id},
            )

    @staticmethod
    def get_by_post_id(db: Session, post_id: int, skip: int = 0, limit: int = 100):
        return CommentRepository.get_by_post_id(db, post_id, skip, limit)

    @staticmethod
    def create(db: Session, comment: schemas.CommentCreate):
        try:
            return CommentRepository.create(db, comment)
        except RecordAlreadyExistsError:
            raise EntityAlreadyExistsError(
                message="Не удалось добавить комментарий.",
                details={"action": "create_comment"},
            )

    @staticmethod
    def update(db: Session, comment_id: int, comment_update: schemas.CommentUpdate):
        try:
            db_comment = CommentRepository.get_by_id(db, comment_id)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Комментарий для обновления не найден.",
                details={"action": "update_comment", "comment_id": comment_id},
            )

        try:
            return CommentRepository.update(db, db_comment, comment_update)
        except RecordAlreadyExistsError:
            raise EntityAlreadyExistsError(
                message="Не удалось обновить комментарий.",
                details={"action": "update_comment", "comment_id": comment_id},
            )

    @staticmethod
    def delete(db: Session, comment_id: int):
        try:
            db_comment = CommentRepository.get_by_id(db, comment_id)
            CommentRepository.delete(db, db_comment)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Комментарий для удаления не найден.",
                details={"action": "delete_comment", "comment_id": comment_id},
            )
