from fastapi import FastAPI
from src.api import categories
from src.infrastructure.database import engine
from src.infrastructure import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Blog FastAPI")

app.include_router(categories.router, prefix="/api/v1/categories", tags=["Categories"])
