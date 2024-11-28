import uuid
from app.application.base_repository import BaseMapper
from app.domain.models.schemma import AgendaEventResponse, MemberCreate, MemberResponse, NotificationResponse, UserCreate
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
            password_hash=user_create.password,
        )

    def to_entity(self, user: User) -> UserResponse:
        return UserResponse(
            username=user.username,
            email=user.email,
        )


class EventMapper(BaseMapper):
    def to_table(self, event_create: EventCreate) -> Event:
        return Event(
            title=event_create.title,
            description=event_create.description,
            start_datetime=event_create.start_time,
            end_datetime=event_create.end_time,
            creator=str(event_create.creator_id),
            # group_id=event_create.group_id,
        )

    def to_entity(self, event: Event) -> EventResponse:
        return EventResponse(
            title=event.title,
            description=event.description,
            start_time=event.start_datetime,
            end_time=event.end_datetime,
            event_type=event.event_type,
            status=event.status,
            creator=uuid.UUID(event.creator_rel),
            group=None
        )


class GroupMapper(BaseMapper):
    def to_table(self, group_create: GroupCreate) -> Group:
        return Group(
            group_name=group_create.name,
            description=group_create.description,
            is_hierarchical=group_create.is_hierarchical,
            parent_group=None
        )

    def to_entity(self, group: Group) -> GroupResponse:
        return GroupResponse(
            id=uuid.UUID(group.id),
            name=group.group_name,
            description=group.description,
            is_hierarchical=False,
            members=[]
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
        )

    def to_table(self, entity):
        raise NotImplementedError


class AgendaMapper(BaseMapper):
    def to_entity(self, event: Event) -> AgendaEventResponse:
        return AgendaEventResponse(
            id=uuid.UUID(event.id),
            title=event.title,
            description=event.description,
            start_time=event.start_datetime,
            end_time=event.end_datetime,
        )

    def to_table(self, entity):
        raise NotImplementedError
