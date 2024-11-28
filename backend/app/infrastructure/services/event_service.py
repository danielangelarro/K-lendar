import inject

from app.application.services.event_service import IEventService
from app.application.repositories.event_repository import IEventRepository
from app.domain.models.schemma import EventCreate, EventResponse


class EventService(IEventService):
    repo_instance: IEventRepository = inject.attr(IEventRepository)

    async def create_event(self, event: EventCreate) -> EventResponse:
        return await self.repo_instance.create(event)

    async def get_event(self, event_id: int) -> EventResponse:
        return await self.repo_instance.get_by_id(event_id)

    async def update_event(self, event_id: int, event_data: EventCreate) -> EventResponse:
        return await self.repo_instance.update(event_id, event_data)

    async def delete_event(self, event_id: int):
        await self.repo_instance.delete(event_id)
