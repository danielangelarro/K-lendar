from datetime import datetime
import uuid
from typing import List

from app.application.repositories.agenda_repository import IAgendaRepository
from app.domain.models.schemma import AgendaEventResponse, UserAgendaResponse
from app.infrastructure.sqlite.tables import Event, Member
from sqlalchemy.future import select
from sqlalchemy import and_


class AgendaRepository(IAgendaRepository):
    async def get_user_agenda(self, user_id: uuid.UUID, start_date: datetime, end_date: datetime) -> UserAgendaResponse:
        db = await self.get_db()
        result = await db.execute(
            select(Event).where(
                Event.start_datetime >= start_date,
                Event.end_datetime <= end_date,
                Event.creator == user_id
            )
        )
        events = result.scalars().all()
        return UserAgendaResponse(user_id=user_id, events=[self.map_event_to_response(event) for event in events])

    async def get_group_agenda(self, group_id: uuid.UUID, start_date: datetime, end_date: datetime) -> List[UserAgendaResponse]:
        db = await self.get_db()
        members = await db.execute(select(Member).where(Member.group_id == group_id))
        member_ids = [member.user_id for member in members.scalars().all()]

        result = await db.execute(
            select(Event).where(
                and_(
                    Event.start_datetime >= start_date,
                    Event.end_datetime <= end_date,
                    Event.creator.in_(member_ids)
                )
            )
        )
        events = result.scalars().all()

        # Agrupar eventos por usuario
        user_agendas = {}
        for event in events:
            if event.creator not in user_agendas:
                user_agendas[event.creator] = []
            user_agendas[event.creator].append(self.map_event_to_response(event))

        return [UserAgendaResponse(user_id=user_id, events=user_agendas[user_id]) for user_id in user_agendas]

    def map_event_to_response(self, event) -> AgendaEventResponse:
        return AgendaEventResponse(
            id=event.id,
            title=event.title,
            description=event.description,
            start_time=event.start_datetime,
            end_time=event.end_datetime
        )
