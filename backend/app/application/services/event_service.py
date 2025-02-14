from typing import List
import uuid

from abc import ABC, abstractmethod

from fastapi import BackgroundTasks
from app.application.base_repository import BaseRepository

from app.domain.models.schemma import EventCreate
from app.domain.models.schemma import EventResponse


class IEventService(ABC):
    repo_instance: BaseRepository = None

    @abstractmethod
    async def create_event(self, event: EventCreate) -> EventResponse:
        pass

    @abstractmethod
    async def create_event_group(self, event: EventCreate, background_tasks: BackgroundTasks) -> EventResponse:
        pass

    @abstractmethod
    async def create_event_hierarchical(self, event: EventCreate, background_tasks: BackgroundTasks) -> EventResponse:
        pass

    @abstractmethod
    async def get_all_event(self, user_id: uuid.UUID) -> List[EventResponse]:
        pass

    @abstractmethod
    async def get_event(self, event_id: uuid.UUID) -> EventResponse:
        pass

    @abstractmethod
    async def update_event(self, event_id: uuid.UUID, event_data: EventCreate) -> EventResponse:
        pass

    @abstractmethod
    async def delete_event(self, event_id: uuid.UUID):
        pass
