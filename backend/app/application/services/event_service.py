import uuid

from abc import ABC, abstractmethod
from app.application.base_repository import BaseRepository

from app.domain.models.schemma import EventCreate
from app.domain.models.schemma import EventResponse


class IEventService(ABC):
    repo_instance: BaseRepository = None

    @abstractmethod
    async def create_event(self, event: EventCreate) -> EventResponse:
        pass

    @abstractmethod
    async def get_event(self, event_id: int) -> EventResponse:
        pass

    @abstractmethod
    async def update_event(self, event_id: int, event_data: EventCreate) -> EventResponse:
        pass

    @abstractmethod
    async def delete_event(self, event_id: int):
        pass
