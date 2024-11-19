from pydantic import BaseModel as PydanticBaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

from app.domain.models.enum import UserRole
from app.domain.models.enum import EventType
from app.domain.models.enum import EventStatus
from app.domain.models.base_model import BaseModelSchema


class UserCreate(BaseModelSchema):
    username: str
    email: EmailStr
    password: str
    role: Optional[UserRole] = UserRole.USER


class UserResponse(BaseModelSchema):
    username: str
    email: str
    role: UserRole


class GroupCreate(BaseModelSchema):
    name: str
    description: Optional[str] = None
    is_hierarchical: bool = False


class GroupResponse(BaseModelSchema):
    name: str
    description: Optional[str]
    is_hierarchical: bool
    members: List[UserResponse] = []


class EventCreate(BaseModelSchema):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    event_type: EventType
    creator_id: int
    group_id: Optional[int] = None
    invitees: List[int] = []


class EventResponse(BaseModelSchema):
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    event_type: EventType
    status: EventStatus
    creator: UserResponse
    group: Optional[GroupResponse] = None
