from datetime import datetime

from pydantic import BaseModel

from app.schema.auth import UserSchema


class TaskSchema(BaseModel):
    id: int
    title: str
    description: str
    is_completed: bool = False
    deadline: datetime | None = None
    user_id: int
    user: UserSchema
    created_at: datetime

    class Config:
        from_attributes = True
