from app.application.base_repository import BaseMapper
from app.domain.models.schemma import UserCreate
from app.domain.models.schemma import UserResponse
from app.domain.models.schemma import EventCreate
from app.domain.models.schemma import EventResponse
from app.infrastructure.sqlite.tables import User
from app.infrastructure.sqlite.tables import Event


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


class EventMapper:
    def to_table(self, event_create: EventCreate) -> Event:
        return Event(
            title=event_create.title,
            description=event_create.description,
            start_datetime=event_create.start_time,
            end_datetime=event_create.end_time,
            creator=event_create.creator_id,
            # Aquí puedes asignar el grupo si es necesario
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
            creator=event.creator_rel,
            group=None
        )
