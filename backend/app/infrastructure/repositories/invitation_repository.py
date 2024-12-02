import uuid
from typing import List
from app.application.repositories.invitation_repository import IInvitationRepository
from app.domain.models.enum import EventStatus
from app.domain.models.schemma import UserResponse
from app.infrastructure.repositories.mapper import InvitationMapper
from app.infrastructure.sqlite.tables import Event, Group, Notification, UserEvent
from app.infrastructure.sqlite.database import get_db
from sqlalchemy.future import select


class InvitationRepository(IInvitationRepository):
    mapper = InvitationMapper()

    async def invite_users(self, event_id: uuid.UUID, user_ids: List[uuid.UUID], group_id: uuid.UUID) -> None:
        async with get_db() as db:
            await db.begin()

            result = await db.execute(select(Event).where(Event.id == str(event_id)))
            event = result.scalars().first()

            result = await db.execute(select(Group).where(Group.id == str(group_id)))
            group = result.scalars().first()

            for user_id in user_ids:
                user_event = UserEvent(user_id=str(user_id), event_id=str(event_id), group_id=str(group_id), status=EventStatus.PENDING.value)
                notification = Notification(
                    recipient=str(user_id),
                    sender=str(user_id),
                    event=str(event.id),
                    priority=False,
                    title="Event Invitations",
                    message=f'New event "{event.title}" assign in {group.group_name}.',
                )
                db.add(user_event)
                db.add(notification)
            try:
                db.flush()
                await self.commit(db)
            except Exception as e:
                await db.rollback()
                raise e

    async def accept_invitation(self, event_id: uuid.UUID, user_id: uuid.UUID) -> None:
        async with get_db() as db:
            user_event = await db.execute(select(UserEvent).where(UserEvent.event_id == str(event_id), UserEvent.user_id == str(user_id)))
            user_event = user_event.scalars().first()
            if user_event:
                user_event.status = EventStatus.CONFIRMED.value

                try:
                    await self.commit(db)
                except Exception as e:
                    await db.rollback()
                    raise e
            else:
                raise Exception("Invitation not found")

    async def decline_invitation(self, event_id: uuid.UUID, user_id: uuid.UUID) -> None:
        async with get_db() as db:
            await db.begin()

            user_event = await db.execute(select(UserEvent).where(UserEvent.event_id == str(event_id), UserEvent.user_id == str(user_id)))
            user_event = user_event.scalars().first()
            if user_event:
                user_event.status = EventStatus.CANCELLED.value
                
                try:
                    await self.commit(db)
                except Exception as e:
                    await db.rollback()
                    raise e
            else:
                raise Exception("Invitation not found")
    
    async def validation_event_in_group(self, event_id: uuid.UUID, members: List[UserResponse]) -> None:
        async with get_db() as db:
            await db.begin()
            user_events = await db.execute(
                select(UserEvent)
                .where(
                    (UserEvent.event_id == str(event_id)) & 
                    (UserEvent.user_id.in_([str(user.id) for user in members]))
                )
            )
            user_events = user_events.scalars().all()

            # Contadores para los resultados de la votación
            votes_for = 0
            votes_against = 0
            abstentions = 0

            # Verificar el estado de cada invitación
            for user_event in user_events:
                if user_event.status == EventStatus.CONFIRMED.value:
                    votes_for += 1
                elif user_event.status == EventStatus.CANCELLED.value:
                    votes_against += 1
                else:
                    abstentions += 1

            # Comprobar si todos los usuarios han aceptado
            if len(user_events) == votes_for:
                # Todos han aceptado
                validation_result = True
            else:
                # No todos han aceptado
                validation_result = False

            # Eliminar todas las invitaciones
            for user_event in user_events:
                await db.delete(user_event)

            # Notificar a los usuarios sobre el resultado de la validación
            notification_message = (
                f"🎉 The task has been {'validated ✅' if validation_result else 'not validated ❌'}. \n"
                f"🗳️ Voting Summary: \n"
                f"   - Votes For: {votes_for} 👍 \n"
                f"   - Votes Against: {votes_against} 👎 \n"
                f"   - Abstentions: {abstentions} 🤷‍♂️"
            )
            
            for user_event in user_events:
                notification = Notification(
                    recipient=str(user_event.user_id),
                    sender=str(user_event.user_id),
                    event=str(event_id),
                    message=notification_message,
                    title="Info"
                )
                db.add(notification)

            try:
                await self.commit(db)
            except Exception as e:
                await db.rollback()
                raise e
