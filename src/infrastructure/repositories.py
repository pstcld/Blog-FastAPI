from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
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
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.User).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, user_id: int):
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if not db_user:
            raise RecordNotFoundError()
        return db_user

    @staticmethod
    def get_by_username(db: Session, username: str):
        db_user = db.query(models.User).filter(models.User.username == username).first()
        if not db_user:
            raise RecordNotFoundError()
        return db_user

    @staticmethod
    def create(db: Session, user_data: dict):
        db_user = models.User(**user_data)
        db.add(db_user)
        try:
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            raise RecordAlreadyExistsError()


class CategoryRepository:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.Category).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, category_id: int):
        db_category = (
            db.query(models.Category).filter(models.Category.id == category_id).first()
        )
        if not db_category:
            raise RecordNotFoundError()
        return db_category

    @staticmethod
    def create(db: Session, category: category_schemas.CategoryCreate):
        db_category = models.Category(**category.model_dump())
        db.add(db_category)
        try:
            db.commit()
            db.refresh(db_category)
            return db_category
        except IntegrityError:
            db.rollback()
            raise RecordAlreadyExistsError()

    @staticmethod
    def update(
        db: Session,
        db_category: models.Category,
        category_update: category_schemas.CategoryUpdate,
    ):
        for key, value in category_update.model_dump().items():
            setattr(db_category, key, value)
        try:
            db.commit()
            db.refresh(db_category)
            return db_category
        except IntegrityError:
            db.rollback()
            raise RecordAlreadyExistsError()

    @staticmethod
    def delete(db: Session, db_category: models.Category):
        db.delete(db_category)
        db.commit()


class LocationRepository:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.Location).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, location_id: int):
        db_location = (
            db.query(models.Location).filter(models.Location.id == location_id).first()
        )
        if not db_location:
            raise RecordNotFoundError()
        return db_location

    @staticmethod
    def create(db: Session, location: location_schemas.LocationCreate):
        db_location = models.Location(**location.model_dump())
        db.add(db_location)
        try:
            db.commit()
            db.refresh(db_location)
            return db_location
        except IntegrityError:
            db.rollback()
            raise RecordAlreadyExistsError()

    @staticmethod
    def update(
        db: Session,
        db_location: models.Location,
        location_update: location_schemas.LocationUpdate,
    ):
        for key, value in location_update.model_dump().items():
            setattr(db_location, key, value)
        try:
            db.commit()
            db.refresh(db_location)
            return db_location
        except IntegrityError:
            db.rollback()
            raise RecordAlreadyExistsError()

    @staticmethod
    def delete(db: Session, db_location: models.Location):
        db.delete(db_location)
        db.commit()


class PostRepository:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.Post).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, post_id: int):
        db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
        if not db_post:
            raise RecordNotFoundError()
        return db_post

    @staticmethod
    def create(db: Session, post: post_schemas.PostCreate):
        db_post = models.Post(**post.model_dump())
        db.add(db_post)
        try:
            db.commit()
            db.refresh(db_post)
            return db_post
        except IntegrityError:
            db.rollback()
            raise RecordAlreadyExistsError()

    @staticmethod
    def update(db: Session, db_post: models.Post, post_update: post_schemas.PostUpdate):
        for key, value in post_update.model_dump().items():
            setattr(db_post, key, value)
        try:
            db.commit()
            db.refresh(db_post)
            return db_post
        except IntegrityError:
            db.rollback()
            raise RecordAlreadyExistsError()

    @staticmethod
    def delete(db: Session, db_post: models.Post):
        db.delete(db_post)
        db.commit()


class CommentRepository:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.Comment).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, comment_id: int):
        db_comment = (
            db.query(models.Comment).filter(models.Comment.id == comment_id).first()
        )
        if not db_comment:
            raise RecordNotFoundError()
        return db_comment

    @staticmethod
    def get_by_post_id(db: Session, post_id: int, skip: int = 0, limit: int = 100):
        return (
            db.query(models.Comment)
            .filter(models.Comment.post_id == post_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def create(db: Session, comment: comment_schemas.CommentCreate):
        db_comment = models.Comment(**comment.model_dump())
        db.add(db_comment)
        try:
            db.commit()
            db.refresh(db_comment)
            return db_comment
        except IntegrityError:
            db.rollback()
            raise RecordAlreadyExistsError()

    @staticmethod
    def update(
        db: Session,
        db_comment: models.Comment,
        comment_update: comment_schemas.CommentUpdate,
    ):
        for key, value in comment_update.model_dump().items():
            setattr(db_comment, key, value)
        try:
            db.commit()
            db.refresh(db_comment)
            return db_comment
        except IntegrityError:
            db.rollback()
            raise RecordAlreadyExistsError()

    @staticmethod
    def delete(db: Session, db_comment: models.Comment):
        db.delete(db_comment)
        db.commit()
