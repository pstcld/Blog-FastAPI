import logging
from fastapi import FastAPI, Request
from src.api import categories, comments, locations, posts, users

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Blog FastAPI")


@app.middleware("http")
async def log_user_actions(request: Request, call_next):
    logger.info(f"Пользователь запросил: {request.method} {request.url}")

    response = await call_next(request)

    logger.info(f"Ответ сервера: статус {response.status_code}")
    return response


app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["Categories"])
app.include_router(locations.router, prefix="/api/v1/locations", tags=["Locations"])
app.include_router(posts.router, prefix="/api/v1/posts", tags=["Posts"])
app.include_router(comments.router, prefix="/api/v1/comments", tags=["Comments"])
