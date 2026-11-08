from fastapi import FastAPI
from src.api import categories, comments, locations, posts, users

app = FastAPI(title="Blog FastAPI")

app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["Categories"])
app.include_router(locations.router, prefix="/api/v1/locations", tags=["Locations"])
app.include_router(posts.router, prefix="/api/v1/posts", tags=["Posts"])
app.include_router(comments.router, prefix="/api/v1/comments", tags=["Comments"])
