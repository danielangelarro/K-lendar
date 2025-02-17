import uuid

from typing import List
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
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
    hashed_password: str


class InviteUserRequest(BaseModelSchema):
    user_ids: List[uuid.UUID]


class AcceptDeclineResponse(BaseModelSchema):
    event_id: uuid.UUID
    user_id: uuid.UUID
    status: InvitationStatus


class GroupCreate(BaseModelSchema):
    name: str
    description: Optional[str] = None
    owner: Optional[UserResponse] = None
    is_hierarchical: bool = False


class GroupResponse(BaseModelSchema):
    name: str
    owner_username: Optional[str] = ""
    cant_members: Optional[int] = 0
    description: Optional[str]
    is_my: Optional[bool] = False
    parent: Optional[str] = None


class EventCreate(BaseModelSchema):
    title: str
    description: Optional[str] = None
    status: str
    start_time: datetime
    end_time: datetime
    event_type: EventType = EventType.PERSONAL
    creator_id: Optional[uuid.UUID] = None
    group_id: Optional[uuid.UUID] = None
    invitees: List[uuid.UUID] = []
    by_owner: bool = True


class EventRequest(BaseModel):
    id: Optional[str] = None
    title: str
    description: Optional[str] = ""
    status: str
    event_type: EventType
    start_time: datetime
    end_time: datetime
    group_name: Optional[str] = None
    by_owner: bool = True


class EventResponse(BaseModelSchema):
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    status: Optional[EventStatus] = None
    event_type: EventType = EventType.PERSONAL
    creator: uuid.UUID
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
    sender: Optional[uuid.UUID] = None
    event: Optional[uuid.UUID] = None
    message: str
    is_read: bool
    priority: bool = True
    date: datetime
    title: str = "Info"
    group: Optional[uuid.UUID] = None


class UserAgendaResponse(BaseModelSchema):
    user_id: uuid.UUID
    name: str
    events: list[EventResponse]


class KeyValueRequest(BaseModel):
    key: str
    value: str


class KeysPayload(BaseModel):
    keys: List[KeyValueRequest]
