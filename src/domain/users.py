from sqlalchemy.ext.asyncio import AsyncSession
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
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100):
        return await UserRepository.get_all(db, skip, limit)

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int):
        try:
            return await UserRepository.get_by_id(db, user_id)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Пользователь не найден.",
                details={"action": "get_user_by_id", "user_id": user_id},
            )

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str):
        try:
            return await UserRepository.get_by_username(db, username)
        except RecordNotFoundError:
            raise EntityNotFoundError(
                message="Пользователь с таким именем не найден.",
                details={"action": "get_user_by_username", "username": username},
            )

    @staticmethod
    async def create(db: AsyncSession, user: schemas.UserCreate):
        hashed_pw = get_password_hash(user.password)

        user_db_data = schemas.UserCreateDB(
            username=user.username,
            email=user.email,
            hashed_password=hashed_pw,
            is_admin=False,
        )

        try:
            return await UserRepository.create(db, user_db_data)
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
    async def authenticate_user(db: AsyncSession, username: str, password: str):
        try:
            user = await UserRepository.get_by_username(db, username)
        except RecordNotFoundError:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user
