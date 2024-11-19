import uuid

from datetime import datetime
from pydantic import BaseModel


class BaseModelSchema(BaseModel):
    id: uuid.UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
