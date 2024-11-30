from typing import List
import uuid
from app.application.repositories.event_repository import IEventRepository
from app.domain.models.schemma import EventCreate, EventResponse
from app.infrastructure.sqlite.tables import Event, UserEvent
from app.infrastructure.sqlite.database import get_db
from app.infrastructure.repositories.mapper import EventMapper
from sqlalchemy.future import select


class EventRepository(IEventRepository):
    mapper = EventMapper()

    async def create(self, event_create: EventCreate) -> EventResponse:
        async with get_db() as db:
            event = self.mapper.to_table(event_create)
            db.add(event)

            await db.flush()

            db.add(UserEvent(
                user_id=str(event_create.creator_id),
                event_id=str(event.id),
                status=event_create.status,
            ))

            try:
                await self.commit(db)
                await self.refresh(db, event)
                
                response = self.mapper.to_entity(event)
                response.status = event_create.status
                
                return response
            except Exception as e:
                await db.rollback()
                raise e

    async def get_by_id(self, event_id: uuid.UUID) -> EventResponse:
        async with get_db() as db:
            result_event = await db.execute(select(Event).where(Event.id == str(event_id)))
            result_event_status = await db.execute(select(UserEvent).where(UserEvent.event_id == str(event_id)))
            
            event = result_event.scalars().first()
            event_status = result_event_status.scalars().first()

            if event:
                response = self.mapper.to_entity(event)
                response.status = event_status.status
                return response
            
            return None

    async def get_by_user_id(self, user_id: uuid.UUID) -> List[EventResponse]:
        async with get_db() as db:
            result = await db.execute(select(Event).where(Event.creator == str(user_id)))
            
            events = result.scalars().all()
            
            for i, event in enumerate(events):
                result_event_status = await db.execute(select(UserEvent).where(UserEvent.event_id == event.id))
                event_status = result_event_status.scalars().first()
                
                events[i] = self.mapper.to_entity(event)
                events[i].status = event_status.status
            
            return events

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
        async with get_db() as db:
            event = await self.get_by_id(str(event_id))
            if event:
                await db.delete(event)
                await self.commit(db)
            else:
                raise Exception("Event not found")
