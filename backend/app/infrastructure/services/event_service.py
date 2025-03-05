import asyncio
from typing import List
import uuid
from fastapi import HTTPException
from fastapi import BackgroundTasks
import inject

from app.application.repositories.invitation_repository import IInvitationRepository
from app.application.services.agenda_service import IAgendaService
from app.application.services.event_service import IEventService
from app.application.repositories.event_repository import IEventRepository
from app.application.services.invitation_service import IInvitationService
from app.application.services.member_service import IMemberService
from app.application.services.notification_service import INotificationService
from app.domain.models.schemma import EventCreate, EventResponse


class EventService(IEventService):
    repo_instance: IEventRepository = inject.attr(IEventRepository)
    repo_invitation: IInvitationRepository = inject.attr(IInvitationRepository)
    notification_service: INotificationService = inject.attr(INotificationService)
    member_service: IMemberService = inject.attr(IMemberService)
    agenda_service: IAgendaService = inject.attr(IAgendaService)
    invitation_service: IInvitationService = inject.attr(IInvitationService)

    async def validate_event(self, event_id, group_members):
        # await asyncio.sleep(30 * 60)  # 30 minutos en segundos
        await asyncio.sleep(10)  # 30 minutos en segundos
        await self.repo_invitation.validation_event_in_group(event_id, group_members)

    async def create_event(self, event: EventCreate) -> EventResponse:
        # Verificamos la disponibilidad del usuario que crea el evento
        user_agenda = await self.agenda_service.get_user_agenda(
            event.creator_id, event.start_time, event.end_time
        )

        # Comprobamos si hay eventos en el rango de tiempo
        if user_agenda.events:
            raise HTTPException(
                status_code=400,
                detail="El usuario ya tiene un evento programado en este rango de tiempo.",
            )

        # Si el usuario está disponible, creamos el evento
        return await self.repo_instance.create(event)

    async def create_event_group(
        self, event: EventCreate, background_tasks: BackgroundTasks
    ) -> EventResponse:
        # Obtenemos los miembros del grupo
        group_members = await self.member_service.get_members(event.group_id)

        # Verificamos la disponibilidad de los miembros
        unavailable_users = []
        for member in group_members:
            user_agenda = await self.agenda_service.get_user_agenda(
                member.id, event.start_time, event.end_time
            )
            if user_agenda.events:  # Si hay eventos en el rango de tiempo
                unavailable_users.append(member.id)

        if unavailable_users:
            raise HTTPException(
                status_code=400,
                detail=f"Los siguientes usuarios no pueden asistir: {unavailable_users}",
            )

        created_event = await self.repo_instance.create(event)

        if event.by_owner:
            for member in group_members:
                if member.id != event.creator_id:
                    await self.repo_instance.asign_event(
                        str(created_event.id),
                        str(member.id),
                        str(event.group_id),
                        event.status,
                    )
        else:
            await self.invitation_service.invite_users(
                event_id=created_event.id,
                user_ids=[
                    member.id
                    for member in group_members
                    if member.id != event.creator_id
                ],
                group_id=event.group_id,
            )

            background_tasks.add_task(
                self.validate_event, created_event.id, group_members
            )

        return created_event

    async def create_event_hierarchical(
        self, event: EventCreate, background_tasks: BackgroundTasks
    ) -> EventResponse:
        # Obtenemos los miembros del grupo y sus grupos hijos
        child_group_members = await self.member_service.get_child_groups(event.group_id)

        # Verificamos la disponibilidad de los miembros del grupo
        unavailable_users = []

        # Verificamos la disponibilidad de los miembros de los grupos hijos
        for member in child_group_members:
            user_agenda = await self.agenda_service.get_user_agenda(
                member.id, event.start_time, event.end_time
            )
            if user_agenda.events:  # Si hay eventos en el rango de tiempo
                unavailable_users.append(member.id)

        if unavailable_users:
            raise HTTPException(
                status_code=400,
                detail=f"Los siguientes usuarios no pueden asistir: {unavailable_users}",
            )

        created_event = await self.repo_instance.create(event)
        background_tasks.add_task(
            self.validate_event, created_event.id, child_group_members
        )

        if event.by_owner:
            for member in child_group_members:
                if member.id != event.creator_id:
                    await self.repo_instance.asign_event(
                        str(created_event.id), str(member.id), str(event.group_id)
                    )
        else:
            await self.invitation_service.invite_users(
                event_id=created_event.id,
                user_ids=[
                    member.id
                    for member in child_group_members
                    if member.id != event.creator_id
                ],
                group_id=event.group_id,
            )

        return created_event

    async def get_event(self, event_id: uuid.UUID) -> EventResponse:
        return await self.repo_instance.get_by_id(event_id)

    async def get_all_event(self, user_id: uuid.UUID) -> List[EventResponse]:
        return await self.repo_instance.get_by_user_id(user_id)

    async def update_event(
        self, event_id: uuid.UUID, event_data: EventCreate
    ) -> EventResponse:
        return await self.repo_instance.update(event_id, event_data)

    async def delete_event(self, event_id: uuid.UUID):
        await self.repo_instance.delete(event_id)
