import logging
from sqlalchemy.orm import Session
from src.infrastructure.database import SessionLocal
from src.infrastructure.models import User
from src.core.security import get_password_hash
from src.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_default_admin():
    db: Session = SessionLocal()
    try:
        admin_exists = db.query(User).filter(User.is_admin == True).first()
        if not admin_exists:
            admin_user = User(
                username=settings.admin_username,
                email=settings.admin_email,
                hashed_password=get_password_hash(settings.admin_password),
                is_admin=True,
            )
            db.add(admin_user)
            db.commit()
            logger.info("Создан дефолтный администратор")
        else:
            logger.info("Дефолтный администратор уже существует")
    except Exception as e:
        logger.error(f"Ошибка при создании администратора: {e}")
    finally:
        db.close()
