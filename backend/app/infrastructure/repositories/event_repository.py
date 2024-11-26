import uuid
from app.application.repositories.event_repository import IEventRepository
from app.domain.models.schemma import EventCreate, EventResponse
from app.infrastructure.sqlite.tables import Event
from app.infrastructure.repositories.mapper import EventMapper
from sqlalchemy.future import select


class EventRepository(IEventRepository):
    mapper = EventMapper()

    async def create(self, event_create: EventCreate) -> EventResponse:
        db = await self.get_db()
        event = self.mapper.to_table(event_create)
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return self.mapper.to_entity(event)

    async def get_by_id(self, event_id: uuid.UUID) -> EventResponse:
        db = await self.get_db()
        result = await db.execute(select(Event).where(Event.id == event_id))
        event = result.scalars().first()
        return self.mapper.to_entity(event) if event else None

    async def update(self, event_id: uuid.UUID, event_data: EventCreate) -> EventResponse:
        db = await self.get_db()
        event = await self.get_by_id(event_id)
        for key, value in event_data.dict().items():
            setattr(event, key, value)
        await db.commit()
        await db.refresh(event)
        return self.mapper.to_entity(event)

    async def delete(self, event_id: uuid.UUID):
        db = await self.get_db()
        event = await self.get_by_id(event_id)
        if event:
            await db.delete(event)
            await db.commit()
        else:
            raise Exception("Event not found")
