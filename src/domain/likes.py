from sqlalchemy.orm import Session
from src.infrastructure import models
from src.core.exceptions.domain_exceptions import EntityNotFoundError


class LikeUseCase:
    @staticmethod
    def toggle_like(
        db: Session, user_id: int, post_id: int = None, comment_id: int = None
    ):
        if (post_id and comment_id) or (not post_id and not comment_id):
            raise ValueError("Необходимо передать либо post_id, либо comment_id")

        if post_id:
            target = db.query(models.Post).filter(models.Post.id == post_id).first()
        else:
            target = (
                db.query(models.Comment).filter(models.Comment.id == comment_id).first()
            )

        if not target:
            raise EntityNotFoundError("Пост или комментарий не найден")

        query = db.query(models.Like).filter(models.Like.user_id == user_id)
        if post_id:
            query = query.filter(models.Like.post_id == post_id)
        if comment_id:
            query = query.filter(models.Like.comment_id == comment_id)

        existing_like = query.first()

        if existing_like:
            db.delete(existing_like)
            db.commit()
            return {"status": "unliked"}

        new_like = models.Like(user_id=user_id, post_id=post_id, comment_id=comment_id)
        db.add(new_like)
        db.commit()
        return {"status": "liked"}

    @staticmethod
    def get_post_likers(db: Session, post_id: int):
        post = db.query(models.Post).filter(models.Post.id == post_id).first()
        if not post:
            raise EntityNotFoundError("Пост не найден")
        return [like.author for like in post.likes]

    @staticmethod
    def get_comment_likers(db: Session, comment_id: int):
        comment = (
            db.query(models.Comment).filter(models.Comment.id == comment_id).first()
        )
        if not comment:
            raise EntityNotFoundError("Комментарий не найден")
        return [like.author for like in comment.likes]

    @staticmethod
    def get_user_liked_posts(db: Session, user_id: int):
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise EntityNotFoundError("Пользователь не найден")
        return [like.post for like in user.likes if like.post_id is not None]

    @staticmethod
    def get_user_liked_comments(db: Session, user_id: int):
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise EntityNotFoundError("Пользователь не найден")
        return [like.comment for like in user.likes if like.comment_id is not None]
