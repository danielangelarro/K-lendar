from datetime import datetime
import uuid
from typing import List

from app.application.repositories.agenda_repository import IAgendaRepository
from app.domain.models.schemma import UserAgendaResponse
from app.infrastructure.repositories.mapper import AgendaMapper
from app.infrastructure.sqlite.tables import Event, Member
from app.infrastructure.sqlite.database import get_db
from sqlalchemy.future import select
from sqlalchemy import and_


class AgendaRepository(IAgendaRepository):
    mapper = AgendaMapper()

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
                events = result.scalars().all()
                return UserAgendaResponse(user_id=user_id, events=[self.mapper(event) for event in events])
            except Exception as e:
                await db.rollback()
                raise e

    async def get_group_agenda(self, group_id: uuid.UUID, start_date: datetime, end_date: datetime) -> List[UserAgendaResponse]:
        async with get_db() as db:
            try:
                members = await db.execute(select(Member).where(Member.group_id == str(group_id)))
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

                user_agendas = {}
                for event in events:
                    if event.creator not in user_agendas:
                        user_agendas[event.creator] = []
                    user_agendas[event.creator].append(self.mapper(event))

                return [UserAgendaResponse(user_id=uuid.UUID(user_id), events=user_agendas[user_id]) for user_id in user_agendas]
            except Exception as e:
                await db.rollback()
                raise e
