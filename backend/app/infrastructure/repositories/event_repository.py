import uuid
from app.application.repositories.event_repository import IEventRepository
from app.domain.models.schemma import EventCreate, EventResponse
from app.infrastructure.sqlite.tables import Event
from app.infrastructure.sqlite.database import get_db
from app.infrastructure.repositories.mapper import EventMapper
from sqlalchemy.future import select


class EventRepository(IEventRepository):
    mapper = EventMapper()

    async def create(self, event_create: EventCreate) -> EventResponse:
        async with get_db() as db:
            event = self.mapper.to_table(event_create)
            db.add(event)
            
            try:
                await self.commit(db)
                await self.refresh(db, event)
                return self.mapper.to_entity(event)
            except Exception as e:
                await db.rollback()
                raise e

    async def get_by_id(self, event_id: uuid.UUID) -> EventResponse:
        async with get_db() as db:
            result = await db.execute(select(Event).where(Event.id == str(event_id)))
            event = result.scalars().first()
            return self.mapper.to_entity(event) if event else None

    async def update(self, event_id: uuid.UUID, event_data: EventCreate) -> EventResponse:
        async with get_db() as db:
            event = await self.get_by_id(str(event_id))
            for key, value in event_data.dict().items():
                setattr(event, key, value)
            
            try:
                await self.commit(db)
                await self.refresh(db, event)
                return self.mapper.to_entity(event)
            except Exception as e:
                await db.rollback()
                raise e

    async def delete(self, event_id: uuid.UUID):
        async with get_db() as db:
            event = await self.get_by_id(str(event_id))
            if event:
                await db.delete(event)
                await self.commit(db)
            else:
                raise Exception("Event not found")
