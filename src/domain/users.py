from sqlalchemy.orm import Session
from src.schemas import users as schemas
from src.infrastructure.repositories import UserRepository
from src.core.security import get_password_hash, verify_password
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
        user_data = user.model_dump()
        password = user_data.pop("password")
        user_data["hashed_password"] = get_password_hash(password)

        try:
            return UserRepository.create(db, user_data)
        except RecordAlreadyExistsError:
            raise EntityAlreadyExistsError(
                message="Пользователь с таким именем или email уже существует.",
                details={
                    "action": "create_user",
                    "username": user.username,
                    "email": user.email,
                },
            )

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str):
        try:
            user = UserRepository.get_by_username(db, username)
        except RecordNotFoundError:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user
