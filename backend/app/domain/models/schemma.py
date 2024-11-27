import uuid

from typing import List
from typing import Optional
from datetime import datetime
from pydantic import EmailStr
from pydantic import BaseModel as PydanticBaseModel

from app.domain.models.enum import UserRole
from app.domain.models.enum import EventType
from app.domain.models.enum import EventStatus
from app.domain.models.enum import InvitationStatus
from app.domain.models.base_model import BaseModelSchema


class Token(PydanticBaseModel):
    access_token: str
    token_type: str


class LoginRequest(PydanticBaseModel):
    username: str
    password: str


class UserCreate(BaseModelSchema):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModelSchema):
    username: str
    email: str


class InviteUserRequest(BaseModelSchema):
    user_ids: List[uuid.UUID]


class AcceptDeclineResponse(BaseModelSchema):
    event_id: uuid.UUID
    user_id: uuid.UUID
    status: InvitationStatus


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
    creator_id: uuid.UUID
    group_id: Optional[uuid.UUID] = None
    invitees: List[uuid.UUID] = []


class EventResponse(BaseModelSchema):
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    event_type: EventType
    status: EventStatus
    creator: UserResponse
    group: Optional[GroupResponse] = None


class MemberCreate(BaseModelSchema):
    user_id: uuid.UUID
    group_id: uuid.UUID


class MemberResponse(BaseModelSchema):
    user_id: uuid.UUID
    group_id: uuid.UUID


class NotificationResponse(BaseModelSchema):
    id: uuid.UUID
    recipient: uuid.UUID
    sender: uuid.UUID
    event: uuid.UUID
    is_read: bool
