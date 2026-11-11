import os
import uuid
from typing import Optional
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas import posts as schemas
from src.infrastructure.repositories import PostRepository, UserRepository
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
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        location_id: Optional[int] = None,
    ):
        return await PostRepository.get_all(
            db, skip=skip, limit=limit, category_id=category_id, location_id=location_id
        )

    @staticmethod
    async def get_by_author_id(
        db: AsyncSession, author_id: int, skip: int = 0, limit: int = 100
    ):
        try:
            await UserRepository.get_by_id(db, author_id)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Пользователь не найден.",
                details={"action": "get_user_posts", "user_id": author_id},
            )
        return await PostRepository.get_by_author_id(
            db, author_id, skip=skip, limit=limit
        )

    @staticmethod
    async def get_by_id(db: AsyncSession, post_id: int):
        try:
            return await PostRepository.get_by_id(db, post_id)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Публикация не найдена.",
                details={"action": "get_post", "post_id": post_id},
            )

    @staticmethod
    async def create(db: AsyncSession, post: schemas.PostCreate):
        try:
            return await PostRepository.create(db, post)
        except RecordAlreadyExistsError:
            raise EntityAlreadyExistsError(
                message="Не удалось создать публикацию.",
                details={"action": "create_post"},
            )

    @staticmethod
    async def update(db: AsyncSession, post_id: int, post_update: schemas.PostUpdate):
        try:
            db_post = await PostRepository.get_by_id(db, post_id)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Публикация для обновления не найдена.",
                details={"action": "update_post", "post_id": post_id},
            )

        try:
            return await PostRepository.update(db, db_post, post_update)
        except RecordAlreadyExistsError:
            raise EntityAlreadyExistsError(
                message="Не удалось обновить публикацию.",
                details={"action": "update_post", "post_id": post_id},
            )

    @staticmethod
    async def delete(db: AsyncSession, post_id: int):
        try:
            db_post = await PostRepository.get_by_id(db, post_id)
            await PostRepository.delete(db, db_post)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Публикация для удаления не найдена.",
                details={"action": "delete_post", "post_id": post_id},
            )

    @staticmethod
    async def upload_image(db: AsyncSession, post_id: int, file: UploadFile):
        try:
            await PostRepository.get_by_id(db, post_id)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Пост не найден",
                details={"action": "upload_image", "post_id": post_id},
            )
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = f"media/{unique_filename}"
        os.makedirs("media", exist_ok=True)

        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)

        image_url = f"/{file_path}"
        return await PostRepository.update_image(db, post_id, image_url)

    @staticmethod
    async def delete_image(db: AsyncSession, post_id: int):
        try:
            post = await PostRepository.get_by_id(db, post_id)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Пост не найден",
                details={"action": "delete_image", "post_id": post_id},
            )
        if post.image:
            file_path = post.image.lstrip("/")
            if os.path.exists(file_path):
                os.remove(file_path)
        return await PostRepository.update_image(db, post_id, None)
