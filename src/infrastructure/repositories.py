from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from typing import Optional

from src.infrastructure import models
from src.schemas import users as user_schemas
from src.schemas import categories as category_schemas
from src.schemas import locations as location_schemas
from src.schemas import posts as post_schemas
from src.schemas import comments as comment_schemas

from src.core.exceptions.database_exceptions import (
    RecordAlreadyExistsError,
    RecordNotFoundError,
)


class UserRepository:
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(models.User).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int):
        result = await db.execute(select(models.User).filter(models.User.id == user_id))
        db_user = result.scalar_one_or_none()
        if not db_user:
            raise RecordNotFoundError()
        return db_user

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str):
        result = await db.execute(
            select(models.User).filter(models.User.username == username)
        )
        db_user = result.scalar_one_or_none()
        if not db_user:
            raise RecordNotFoundError()
        return db_user

    @staticmethod
    async def create(db: AsyncSession, user: user_schemas.UserCreateDB):
        db_user = models.User(**user.model_dump())
        db.add(db_user)
        try:
            await db.commit()
            await db.refresh(db_user)
            return db_user
        except IntegrityError:
            await db.rollback()
            raise RecordAlreadyExistsError()


class CategoryRepository:
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(models.Category).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, category_id: int):
        result = await db.execute(
            select(models.Category).filter(models.Category.id == category_id)
        )
        db_category = result.scalar_one_or_none()
        if not db_category:
            raise RecordNotFoundError()
        return db_category

    @staticmethod
    async def create(db: AsyncSession, category: category_schemas.CategoryCreate):
        db_category = models.Category(**category.model_dump())
        db.add(db_category)
        try:
            await db.commit()
            await db.refresh(db_category)
            return db_category
        except IntegrityError:
            await db.rollback()
            raise RecordAlreadyExistsError()

    @staticmethod
    async def update(
        db: AsyncSession,
        db_category: models.Category,
        category_update: category_schemas.CategoryUpdate,
    ):
        for key, value in category_update.model_dump().items():
            setattr(db_category, key, value)
        try:
            await db.commit()
            await db.refresh(db_category)
            return db_category
        except IntegrityError:
            await db.rollback()
            raise RecordAlreadyExistsError()

    @staticmethod
    async def delete(db: AsyncSession, db_category: models.Category):
        await db.delete(db_category)
        await db.commit()


class LocationRepository:
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(models.Location).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, location_id: int):
        result = await db.execute(
            select(models.Location).filter(models.Location.id == location_id)
        )
        db_location = result.scalar_one_or_none()
        if not db_location:
            raise RecordNotFoundError()
        return db_location

    @staticmethod
    async def create(db: AsyncSession, location: location_schemas.LocationCreate):
        db_location = models.Location(**location.model_dump())
        db.add(db_location)
        try:
            await db.commit()
            await db.refresh(db_location)
            return db_location
        except IntegrityError:
            await db.rollback()
            raise RecordAlreadyExistsError()

    @staticmethod
    async def update(
        db: AsyncSession,
        db_location: models.Location,
        location_update: location_schemas.LocationUpdate,
    ):
        for key, value in location_update.model_dump().items():
            setattr(db_location, key, value)
        try:
            await db.commit()
            await db.refresh(db_location)
            return db_location
        except IntegrityError:
            await db.rollback()
            raise RecordAlreadyExistsError()

    @staticmethod
    async def delete(db: AsyncSession, db_location: models.Location):
        await db.delete(db_location)
        await db.commit()


class PostRepository:
    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        location_id: Optional[int] = None,
    ):
        stmt = select(models.Post).options(selectinload(models.Post.author))
        if category_id is not None:
            stmt = stmt.filter(models.Post.category_id == category_id)
        if location_id is not None:
            stmt = stmt.filter(models.Post.location_id == location_id)

        stmt = stmt.order_by(models.Post.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_author_id(
        db: AsyncSession, author_id: int, skip: int = 0, limit: int = 100
    ):
        stmt = (
            select(models.Post)
            .options(selectinload(models.Post.author))
            .filter(models.Post.author_id == author_id)
            .order_by(models.Post.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, post_id: int):
        stmt = (
            select(models.Post)
            .options(selectinload(models.Post.author))
            .filter(models.Post.id == post_id)
        )
        result = await db.execute(stmt)
        db_post = result.scalar_one_or_none()
        if not db_post:
            raise RecordNotFoundError()
        return db_post

    @staticmethod
    async def create(db: AsyncSession, post: post_schemas.PostCreate):
        db_post = models.Post(**post.model_dump())
        db.add(db_post)
        try:
            await db.commit()
            await db.refresh(db_post)
            return await PostRepository.get_by_id(db, db_post.id)
        except IntegrityError:
            await db.rollback()
            raise RecordAlreadyExistsError()

    @staticmethod
    async def update(
        db: AsyncSession, db_post: models.Post, post_update: post_schemas.PostUpdate
    ):
        update_data = post_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_post, key, value)
        try:
            await db.commit()
            await db.refresh(db_post)
            return await PostRepository.get_by_id(db, db_post.id)
        except IntegrityError:
            await db.rollback()
            raise RecordAlreadyExistsError()

    @staticmethod
    async def delete(db: AsyncSession, db_post: models.Post):
        await db.delete(db_post)
        await db.commit()

    @staticmethod
    async def update_image(db: AsyncSession, post_id: int, image_url: Optional[str]):
        post = await PostRepository.get_by_id(db, post_id)
        if post:
            post.image = image_url
            await db.commit()
            await db.refresh(post)
        return post


class CommentRepository:
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100):
        stmt = (
            select(models.Comment)
            .options(selectinload(models.Comment.author))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, comment_id: int):
        stmt = (
            select(models.Comment)
            .options(selectinload(models.Comment.author))
            .filter(models.Comment.id == comment_id)
        )
        result = await db.execute(stmt)
        db_comment = result.scalar_one_or_none()
        if not db_comment:
            raise RecordNotFoundError()
        return db_comment

    @staticmethod
    async def get_by_post_id(
        db: AsyncSession, post_id: int, skip: int = 0, limit: int = 100
    ):
        stmt = (
            select(models.Comment)
            .options(selectinload(models.Comment.author))
            .filter(models.Comment.post_id == post_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, comment: comment_schemas.CommentCreate):
        comment_data = comment.model_dump()
        comment_data["author_id"] = comment.author_id
        comment_data["post_id"] = comment.post_id
        db_comment = models.Comment(**comment_data)
        db.add(db_comment)
        try:
            await db.commit()
            await db.refresh(db_comment)
            return await CommentRepository.get_by_id(db, db_comment.id)
        except IntegrityError:
            await db.rollback()
            raise RecordAlreadyExistsError()

    @staticmethod
    async def update(
        db: AsyncSession,
        db_comment: models.Comment,
        comment_update: comment_schemas.CommentUpdate,
    ):
        for key, value in comment_update.model_dump().items():
            setattr(db_comment, key, value)
        try:
            await db.commit()
            await db.refresh(db_comment)
            return await CommentRepository.get_by_id(db, db_comment.id)
        except IntegrityError:
            await db.rollback()
            raise RecordAlreadyExistsError()

    @staticmethod
    async def delete(db: AsyncSession, db_comment: models.Comment):
        await db.delete(db_comment)
        await db.commit()
