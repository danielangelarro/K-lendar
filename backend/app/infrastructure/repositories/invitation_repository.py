import uuid
from typing import List
from app.application.repositories.invitation_repository import IInvitationRepository
from app.domain.models.enum import EventStatus
from app.infrastructure.repositories.mapper import InvitationMapper
from app.infrastructure.sqlite.tables import UserEvent
from app.infrastructure.sqlite.database import get_db
from sqlalchemy.future import select


class InvitationRepository(IInvitationRepository):
    mapper = InvitationMapper()

    async def invite_users(self, event_id: uuid.UUID, user_ids: List[uuid.UUID]) -> None:
        async with get_db() as db:
            for user_id in user_ids:
                user_event = UserEvent(user_id=str(user_id), event_id=str(event_id), status=EventStatus.PENDING)
                db.add(user_event)
            try:
                await self.commit(db)
            except Exception as e:
                await db.rollback()
                raise e

    async def accept_invitation(self, event_id: uuid.UUID, user_id: uuid.UUID) -> None:
        async with get_db() as db:
            user_event = await db.execute(select(UserEvent).where(UserEvent.event_id == str(event_id), UserEvent.user_id == str(user_id)))
            user_event = user_event.scalars().first()
            if user_event:
                user_event.status = EventStatus.ACCEPTED

                try:
                    await self.commit(db)
                except Exception as e:
                    await db.rollback()
                    raise e
            else:
                raise Exception("Invitation not found")

    async def decline_invitation(self, event_id: uuid.UUID, user_id: uuid.UUID) -> None:
        async with get_db() as db:
            user_event = await db.execute(select(UserEvent).where(UserEvent.event_id == str(event_id), UserEvent.user_id == str(user_id)))
            user_event = user_event.scalars().first()
            if user_event:
                user_event.status = EventStatus.CANCELLED
                
                try:
                    await self.commit(db)
                except Exception as e:
                    await db.rollback()
                    raise e
            else:
                raise Exception("Invitation not found")
