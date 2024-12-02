from datetime import datetime
import uuid
from typing import List

from app.application.repositories.agenda_repository import IAgendaRepository
from app.domain.models.schemma import UserAgendaResponse
from app.infrastructure.repositories.mapper import EventMapper, GroupMapper
from app.infrastructure.sqlite.tables import Event, Group, Member, User, UserEvent
from app.infrastructure.sqlite.database import get_db
from sqlalchemy.future import select
from sqlalchemy import and_


class AgendaRepository(IAgendaRepository):
    mapper = EventMapper()
    group_mapper = GroupMapper()

    async def get_user_agenda(self, user_id: uuid.UUID, start_date: datetime, end_date: datetime) -> UserAgendaResponse:
        async with get_db() as db:
            try:
                result = await db.execute(
                    select(Event).where(
                        Event.start_datetime >= start_date,
                        Event.end_datetime <= end_date,
                        Event.creator == str(user_id)
                    )
                )
                result_events = result.scalars().all()

                result = await db.execute(select(User).where(User.id == str(user_id)))
                user = result.scalars().first()

                events = []
                
                for item in result_events:
                    result_event_status = await db.execute(select(UserEvent).where(UserEvent.event_id == item.id))
                    event_status = result_event_status.scalars().first()
                    
                    result = await db.execute(select(Group).where(Group.id == event_status.group_id))
                    group = result.scalars().first()

                    event = self.mapper.to_entity(item)
                    event.status = event_status.status

                    if group:
                        event.group = self.group_mapper.to_entity(group)

                    events.append(event)

                return UserAgendaResponse(user_id=user_id, name=user.username, events=events)
            except Exception as e:
                await db.rollback()
                raise e

    async def get_group_agenda(self, group_id: uuid.UUID, start_date: datetime, end_date: datetime) -> List[UserAgendaResponse]:
        async with get_db() as db:
            try:
                members = await db.execute(select(Member).where(Member.group_id == str(group_id)))
                member_ids = [member.user_id for member in members.scalars().all()]

                response = [
                    await self.get_user_agenda(uuid.UUID(member_id), start_date, end_date)
                    for member_id in member_ids
                ]

                return response
            except Exception as e:
                await db.rollback()
                raise e
