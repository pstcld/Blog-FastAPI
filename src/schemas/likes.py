from pydantic import BaseModel, ConfigDict
from typing import Optional


class LikeResponse(BaseModel):
    id: int
    user_id: int
    post_id: Optional[int] = None
    comment_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
