from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.infrastructure import models
from src.core.exceptions.domain_exceptions import EntityNotFoundError


class LikeUseCase:
    @staticmethod
    async def toggle_like(
        db: AsyncSession, user_id: int, post_id: int = None, comment_id: int = None
    ):
        if (post_id and comment_id) or (not post_id and not comment_id):
            raise ValueError("Необходимо передать либо post_id, либо comment_id")

        if post_id:
            target_res = await db.execute(
                select(models.Post).filter(models.Post.id == post_id)
            )
        else:
            target_res = await db.execute(
                select(models.Comment).filter(models.Comment.id == comment_id)
            )

        if not target_res.scalar_one_or_none():
            raise EntityNotFoundError("Пост или комментарий не найден")

        stmt = select(models.Like).filter(models.Like.user_id == user_id)
        if post_id:
            stmt = stmt.filter(models.Like.post_id == post_id)
        if comment_id:
            stmt = stmt.filter(models.Like.comment_id == comment_id)

        result = await db.execute(stmt)
        existing_like = result.scalar_one_or_none()

        if existing_like:
            await db.delete(existing_like)
            await db.commit()
            return {"status": "unliked"}

        new_like = models.Like(user_id=user_id, post_id=post_id, comment_id=comment_id)
        db.add(new_like)
        await db.commit()
        return {"status": "liked"}

    @staticmethod
    async def get_post_likers(db: AsyncSession, post_id: int):
        stmt = (
            select(models.User)
            .join(models.Like, models.User.id == models.Like.user_id)
            .filter(models.Like.post_id == post_id)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_comment_likers(db: AsyncSession, comment_id: int):
        stmt = (
            select(models.User)
            .join(models.Like, models.User.id == models.Like.user_id)
            .filter(models.Like.comment_id == comment_id)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_user_liked_posts(db: AsyncSession, user_id: int):
        stmt = (
            select(models.Post)
            .options(selectinload(models.Post.author))
            .join(models.Like, models.Post.id == models.Like.post_id)
            .filter(models.Like.user_id == user_id)
            .order_by(models.Post.created_at.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_user_liked_comments(db: AsyncSession, user_id: int):
        stmt = (
            select(models.Comment)
            .options(selectinload(models.Comment.author))
            .join(models.Like, models.Comment.id == models.Like.comment_id)
            .filter(models.Like.user_id == user_id)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
