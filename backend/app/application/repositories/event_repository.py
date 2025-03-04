import uuid

from abc import abstractmethod
from app.application.base_repository import BaseRepository
from app.domain.models.schemma import EventCreate
from app.domain.models.schemma import EventResponse


class IEventRepository(BaseRepository):
    @abstractmethod
    async def create(self, event_create: EventCreate) -> EventResponse:        
        pass

    @abstractmethod
    async def asign_event(self, event_id: str, user_id: str, group_id: str, status: str) -> None:
        pass

    @abstractmethod
    async def update(self, event_id: uuid.UUID, event_data: EventCreate) -> EventResponse:
        pass

    @abstractmethod
    async def get_by_id(self, event_id: uuid.UUID) -> EventResponse:
        pass

    @abstractmethod
    async def delete(self, event_id: uuid.UUID):
        pass
