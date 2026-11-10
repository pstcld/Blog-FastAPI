from sqlalchemy.orm import Session
from src.schemas import users as schemas
from src.infrastructure.repositories import UserRepository
from src.core.exceptions.database_exceptions import (
    RecordAlreadyExistsError,
    RecordNotFoundError,
)
from src.core.exceptions.domain_exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)


class UserUseCase:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return UserRepository.get_all(db, skip, limit)

    @staticmethod
    def get_by_id(db: Session, user_id: int):
        try:
            return UserRepository.get_by_id(db, user_id)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Пользователь не найден.",
                details={"action": "get_user_by_id", "user_id": user_id},
            )

    @staticmethod
    def get_by_username(db: Session, username: str):
        try:
            return UserRepository.get_by_username(db, username)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Пользователь с таким именем не найден.",
                details={"action": "get_user_by_username", "username": username},
            )

    @staticmethod
    def create(db: Session, user: schemas.UserCreate):
        try:
            return UserRepository.create(db, user)
        except RecordAlreadyExistsError:
            raise EntityAlreadyExistsError(
                message="Пользователь с таким именем или email уже существует.",
                details={
                    "action": "create_user",
                    "username": user.username,
                    "email": user.email,
                },
            )
