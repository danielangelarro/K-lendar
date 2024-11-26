import uuid

from abc import ABC, abstractmethod
from app.domain.models.schemma import EventCreate
from app.domain.models.schemma import EventResponse


class IEventRepository(ABC):
    @abstractmethod
    async def create(self, event_create: EventCreate) -> EventResponse:        
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
