from typing import List, Dict
import uuid
from datetime import datetime
from app.application.base_repository import BaseMapper
from app.domain.models.enum import EventStatus
from app.domain.models.schemma import EventResponse, MemberCreate, MemberResponse, NotificationResponse, UserCreate
from app.domain.models.schemma import UserResponse
from app.domain.models.schemma import EventCreate
from app.domain.models.schemma import EventResponse
from app.domain.models.schemma import GroupCreate
from app.domain.models.schemma import GroupResponse
from app.infrastructure.sqlite.tables import Member, Notification, User, UserEvent
from app.infrastructure.sqlite.tables import Event
from app.infrastructure.sqlite.tables import Group
from app.infrastructure.sqlite.utils import generate_unique_uuid, generate_uuid


class UserMapper(BaseMapper):
    def to_table(self, user_create: UserCreate) -> Dict:
        return {
            "id": generate_uuid(),
            "username": user_create.username,
            "email": user_create.email,
            "password": user_create.password,
        }

    def to_entity(self, user: dict) -> UserResponse:
        return UserResponse(
            id=user['id'],
            username=user['username'],
            email=user['email'],
            hashed_password=user['password'],
        )


class EventMapper(BaseMapper):
    def to_table(self, event_create: EventCreate) -> Dict:
        return {
            "id": generate_uuid(),
            "title": event_create.title,
            "description": event_create.description,
            "start_datetime": event_create.start_time.isoformat(),  # Datetime a string ISO
            "end_datetime": event_create.end_time.isoformat(),
            "event_type": event_create.event_type.value,  # Enum a string
            "creator": str(event_create.creator_id),  # UUID a string
        }

    def to_entity(self, event: dict) -> EventResponse:
        return EventResponse(
            id=event['id'],
            title=event['title'],
            description=event['description'],
            start_time=event['start_datetime'],
            end_time=event['end_datetime'],
            event_type=event['event_type'],
            creator=uuid.UUID(event['creator']),
            group=None
        )


class GroupMapper(BaseMapper):
    def to_table(self, group_create: GroupCreate) -> Dict:
        return {
            "id": generate_uuid(),
            "group_name": group_create.name,
            "description": group_create.description,
            "owner_id": str(group_create.owner.id),  # UUID a string
        }

    def to_entity(self, group: dict) -> GroupResponse:
        return GroupResponse(
            id=uuid.UUID(group['id']),
            name=group['group_name'],
            description=group['description'],
        )


class MemberMapper(BaseMapper):
    def to_table(self, member_create: MemberCreate) -> Dict:
        return {
            "id": generate_unique_uuid(member_create.user_id, member_create.group_id),
            "user_id": str(member_create.user_id),
            "group_id": str(member_create.group_id),
        }

    def to_entity(self, member: dict) -> MemberResponse:
        return MemberResponse(
            user_id=uuid.UUID(member['user_id']),
            group_id=uuid.UUID(member['group_id']),
        )


class InvitationMapper(BaseMapper):
    def to_table(self, user_event: UserEvent) -> Dict:
        return {
            "id": generate_uuid(),
            "user_id": str(user_event.user_id),  # UUID a string
            "event_id": str(user_event.event_id),
            "status": user_event.status,
        }

    def to_entity(self, data):
        raise NotImplementedError


class NotificationMapper(BaseMapper):
    def to_entity(self, notification: Notification) -> NotificationResponse:
        return NotificationResponse(
            id=uuid.UUID(notification.id),
            recipient=uuid.UUID(notification.recipient),
            message=notification.message,
            is_read=notification.is_read,
            priority=notification.priority if notification.priority is not None else True,
            date=notification.created_at,
            title=notification.title if notification.title else "Info",
            event=notification.event,
        )

    def to_table(self, entity):
        raise NotImplementedError