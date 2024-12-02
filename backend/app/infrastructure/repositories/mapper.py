from typing import List
import uuid
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


class UserMapper(BaseMapper):
    def to_table(self, user_create: UserCreate) -> User:
        return User(
            username=user_create.username,
            email=user_create.email,
            password=user_create.password,
        )

    def to_entity(self, user: User) -> UserResponse:
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            hashed_password=user.password,
        )


class EventMapper(BaseMapper):
    def to_table(self, event_create: EventCreate) -> Event:
        return Event(
            title=event_create.title,
            description=event_create.description,
            start_datetime=event_create.start_time,
            end_datetime=event_create.end_time,
            event_type=event_create.event_type.value,
            creator=str(event_create.creator_id),
        )

    def to_entity(self, event: Event) -> EventResponse:
        return EventResponse(
            id=event.id,
            title=event.title,
            description=event.description,
            start_time=event.start_datetime,
            end_time=event.end_datetime,
            event_type=event.event_type,
            creator=uuid.UUID(event.creator),
            group=None
        )


class GroupMapper(BaseMapper):
    def to_table(self, group_create: GroupCreate) -> Group:
        return Group(
            group_name=group_create.name,
            description=group_create.description,
            owner_id=str(group_create.owner.id),
        )

    def to_entity(self, group: Group) -> GroupResponse:
        return GroupResponse(
            id=uuid.UUID(group.id),
            name=group.group_name,
            description=group.description,
        )


class MemberMapper(BaseMapper):
    def to_table(self, member_create: MemberCreate) -> Member:
        return Member(
            user_id=str(member_create.user_id),
            group_id=str(member_create.group_id),
        )

    def to_entity(self, member: Member) -> MemberResponse:
        return MemberResponse(
            user_id=uuid.UUID(member.user_id),
            group_id=uuid.UUID(member.group_id),
        )


class InvitationMapper(BaseMapper):
    def to_table(self, user_event: UserEvent) -> UserEvent:
        return UserEvent(
            user_id=str(user_event.user_id),
            event_id=str(user_event.event_id),
            status=user_event.status,
        )

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
