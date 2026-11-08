from pydantic import BaseModel, Field
from datetime import datetime


class PublishedCreatedBase(BaseModel):
    is_published: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
