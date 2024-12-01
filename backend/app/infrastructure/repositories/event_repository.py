from enum import Enum
from typing import List
import uuid

from fastapi import HTTPException
from sqlalchemy import case
from sqlalchemy.future import select

from app.application.repositories.event_repository import IEventRepository
from app.domain.models.enum import EventStatus
from app.domain.models.schemma import EventCreate, EventResponse
from app.infrastructure.sqlite.tables import Event, Group, Member, Notification, UserEvent
from app.infrastructure.sqlite.database import get_db
from app.infrastructure.repositories.mapper import EventMapper, GroupMapper


class EventRepository(IEventRepository):
    mapper = EventMapper()
    group_mapper = GroupMapper()

    async def create(self, event_create: EventCreate) -> EventResponse:
        async with get_db() as db:
            event = self.mapper.to_table(event_create)
            db.add(event)

            await db.flush()

            db.add(UserEvent(
                user_id=str(event_create.creator_id),
                event_id=str(event.id),
                status=event_create.status,
                group_id=str(event_create.group_id),
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
    
    async def asign_event(self, event_id: str, user_id: str, group_id: str) -> None:
        async with get_db() as db:
            try:
                await db.begin()

                user_event = UserEvent(
                    user_id=user_id,
                    event_id=event_id,
                    status=EventStatus.PENDING.value,
                    group_id=group_id,
                )

                result = await db.execute(select(Event).where(Event.id == str(event_id)))
                event = result.scalars().first()

                result = await db.execute(select(Group).where(Group.id == str(group_id)))
                group = result.scalars().first()

                is_owner = event.creator == group.owner_id

                notification = Notification(
                    recipient=user_id,
                    sender=user_id,
                    event=event_id,
                    priority=is_owner,
                    message=f'New event "{event.title}" assign in {group.group_name}.',
                )

                db.add(user_event)
                db.add(notification)

                await self.commit(db)
                await self.refresh(db, user_event)
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
            result = await db.execute(
                select(Event)
                .join(UserEvent, Event.id == UserEvent.event_id)
                .where(UserEvent.user_id == str(user_id))
            )
            
            results = result.scalars().all()
            events = []
            
            for item in results:
                result_event_status = await db.execute(select(UserEvent).where(UserEvent.event_id == item.id))
                event_status = result_event_status.scalars().first()
                
                result = await db.execute(select(Group).where(Group.id == event_status.group_id))
                group = result.scalars().first()

                event = self.mapper.to_entity(item)
                event.status = event_status.status

                if group:
                    event.group = self.group_mapper.to_entity(group)

                events.append(event)
            
            return events

    async def update(self, event_id: uuid.UUID, event_data: EventCreate) -> EventResponse:
        async with get_db() as db:
            try:
                result = await db.execute(select(Event).where(Event.id == str(event_id)))
                event = result.scalars().first()

                if not event:
                    raise HTTPException(status_code=404, detail="Event not found")

                update_data = event_data.dict(exclude_unset=True)
            
                for key, value in update_data.items():
                    if hasattr(event, key):
                        if key == "event_type":
                            setattr(event, key, value.value)
                        else:
                            setattr(event, key, value)
                
                await db.flush()
                await self.commit(db)
                await self.refresh(db, event)

                response = self.mapper.to_entity(event)
                response.status = event_data.status
                
                return response
            except Exception as e:
                await db.rollback()
                raise HTTPException(status_code=500, detail=str(e))

    async def delete(self, event_id: uuid.UUID):
        async with get_db() as db:
            result = await db.execute(select(Event).where(Event.id == str(event_id)))
            event = result.scalars().first()
            if event:
                await db.delete(event)
                await self.commit(db)
            else:
                raise Exception("Event not found")
