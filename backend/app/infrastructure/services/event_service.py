from typing import List
import uuid
from fastapi import HTTPException
import inject

from app.application.services.agenda_service import IAgendaService
from app.application.services.event_service import IEventService
from app.application.repositories.event_repository import IEventRepository
from app.application.services.member_service import IMemberService
from app.application.services.notification_service import INotificationService
from app.domain.models.schemma import EventCreate, EventResponse


class EventService(IEventService):
    repo_instance: IEventRepository = inject.attr(IEventRepository)
    notification_service: INotificationService = inject.attr(INotificationService)
    member_service: IMemberService = inject.attr(IMemberService)
    agenda_service: IAgendaService = inject.attr(IAgendaService)

    async def create_event(self, event: EventCreate) -> EventResponse:
        # Verificamos la disponibilidad del usuario que crea el evento
        user_agenda = await self.agenda_service.get_user_agenda(event.creator_id, event.start_time, event.end_time)
        
        # Comprobamos si hay eventos en el rango de tiempo
        if user_agenda.events:
            raise HTTPException(status_code=400, detail="El usuario ya tiene un evento programado en este rango de tiempo.")

        # Si el usuario está disponible, creamos el evento
        return await self.repo_instance.create(event)

    async def create_event_group(self, event: EventCreate) -> EventResponse:
        # Obtenemos los miembros del grupo
        group_members = await self.member_service.get_members(event.group_id)

        # Verificamos la disponibilidad de los miembros
        unavailable_users = []
        for member in group_members:
            user_agenda = await self.agenda_service.get_user_agenda(member.id, event.start_time, event.end_time)
            if user_agenda.events:  # Si hay eventos en el rango de tiempo
                unavailable_users.append(member.id)

        if unavailable_users:
            raise HTTPException(status_code=400, detail=f"Los siguientes usuarios no pueden asistir: {unavailable_users}")

        created_event = await self.repo_instance.create(event)

        for member in group_members:
            if member.id != event.creator_id:
                await self.repo_instance.asign_event(str(created_event.id), str(member.id), str(event.group_id))

        return created_event

    async def create_event_hierarchical(self, event: EventCreate) -> EventResponse:
        # Obtenemos los miembros del grupo y sus grupos hijos
        group_members = await self.member_service.get_members(event.group_id)
        child_groups = await self.member_service.get_child_groups(event.group_id)

        # Verificamos la disponibilidad de los miembros del grupo
        unavailable_users = []
        for member in group_members:
            user_agenda = await self.agenda_service.get_user_agenda(member.user_id, event.start_time, event.end_time)
            if user_agenda.events:  # Si hay eventos en el rango de tiempo
                unavailable_users.append(member.user_id)

        # Verificamos la disponibilidad de los miembros de los grupos hijos
        for child_group in child_groups:
            child_group_members = await self.member_service.get_members(child_group.id)
            for member in child_group_members:
                user_agenda = await self.agenda_service.get_user_agenda(member.user_id, event.start_time, event.end_time)
                if user_agenda.events:  # Si hay eventos en el rango de tiempo
                    unavailable_users.append(member.user_id)

        if unavailable_users:
            raise HTTPException(status_code=400, detail=f"Los siguientes usuarios no pueden asistir: {unavailable_users}")

        created_event = await self.repo_instance.create(event)

        # Enviamos notificaciones a todos los miembros del grupo y de los grupos hijos
        notification_response = await self.notification_service.send_event_notification(
            event.group_id, created_event.id)

        return created_event

    async def get_event(self, event_id: uuid.UUID) -> EventResponse:
        return await self.repo_instance.get_by_id(event_id)
    
    async def get_all_event(self, user_id: uuid.UUID) -> List[EventResponse]:
        return await self.repo_instance.get_by_user_id(user_id)

    async def update_event(self, event_id: uuid.UUID, event_data: EventCreate) -> EventResponse:
        return await self.repo_instance.update(event_id, event_data)

    async def delete_event(self, event_id: uuid.UUID):
        await self.repo_instance.delete(event_id)
