from sqlalchemy.ext.asyncio import AsyncSession
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
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100):
        return await CommentRepository.get_all(db, skip, limit)

    @staticmethod
    async def get_by_id(db: AsyncSession, comment_id: int):
        try:
            return await CommentRepository.get_by_id(db, comment_id)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Комментарий не найден.",
                details={"action": "get_comment", "comment_id": comment_id},
            )

    @staticmethod
    async def get_by_post_id(
        db: AsyncSession, post_id: int, skip: int = 0, limit: int = 100
    ):
        return await CommentRepository.get_by_post_id(db, post_id, skip, limit)

    @staticmethod
    async def create(db: AsyncSession, comment: schemas.CommentCreate):
        try:
            return await CommentRepository.create(db, comment)
        except RecordAlreadyExistsError:
            raise EntityAlreadyExistsError(
                message="Не удалось добавить комментарий.",
                details={"action": "create_comment"},
            )

    @staticmethod
    async def update(
        db: AsyncSession, comment_id: int, comment_update: schemas.CommentUpdate
    ):
        try:
            db_comment = await CommentRepository.get_by_id(db, comment_id)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Комментарий для обновления не найден.",
                details={"action": "update_comment", "comment_id": comment_id},
            )

        try:
            return await CommentRepository.update(db, db_comment, comment_update)
        except RecordAlreadyExistsError:
            raise EntityAlreadyExistsError(
                message="Не удалось обновить комментарий.",
                details={"action": "update_comment", "comment_id": comment_id},
            )

    @staticmethod
    async def delete(db: AsyncSession, comment_id: int):
        try:
            db_comment = await CommentRepository.get_by_id(db, comment_id)
            await CommentRepository.delete(db, db_comment)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Комментарий для удаления не найден.",
                details={"action": "delete_comment", "comment_id": comment_id},
            )
