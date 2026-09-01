import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatCreate(BaseModel):
    title: str


class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime