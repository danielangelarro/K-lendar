import json
import uuid
from typing import List
from fastapi import HTTPException

from app.application.repositories.invitation_repository import IInvitationRepository
from app.domain.models.enum import EventStatus
from app.domain.models.schemma import UserResponse
from app.infrastructure.repositories.mapper import InvitationMapper
from app.infrastructure.sqlite.utils import generate_uuid
from app.settings import settings


class InvitationRepository(IInvitationRepository):
    mapper = InvitationMapper()

    async def invite_users(
        self, event_id: uuid.UUID, user_ids: List[uuid.UUID], group_id: uuid.UUID
    ) -> None:
        # Recuperar el evento y el grupo desde el anillo
        event_json = settings.node.ref.retrieve_key(f"events:{event_id}")
        if not event_json:
            raise HTTPException(status_code=404, detail="Event not found")
        event = json.loads(event_json)

        group_json = settings.node.ref.retrieve_key(f"groups:{group_id}")
        if not group_json:
            raise HTTPException(status_code=404, detail="Group not found")
        group = json.loads(group_json)

        for user_id in user_ids:
            # Crear la invitación (UserEvent) con estado "pending"
            user_event = {
                "id": str(generate_uuid()),
                "user_id": str(user_id),
                "event_id": str(event_id),
                "group_id": str(group_id),
                "status": EventStatus.PENDING.value,
                "created_at": None,
                "updated_at": None,
            }
            settings.node.ref.store_key(
                f"user_event:{user_event['id']}", json.dumps(user_event)
            )
            # Crear la notificación correspondiente
            notification = {
                "id": str(generate_uuid()),
                "recipient": str(user_id),
                "sender": str(user_id),
                "event": str(event["id"]),
                "priority": False,
                "title": "Event Invitations",
                "message": f'New event "{event["title"]}" assign in {group["group_name"]}.',
                "is_read": False,
            }
            settings.node.ref.store_key(
                f"notification:{notification['id']}", json.dumps(notification)
            )

    async def accept_invitation(self, event_id: uuid.UUID, user_id: uuid.UUID) -> None:
        query_payload = json.dumps(
            {
                "table": "user_event",
                "filters": {"event_id": str(event_id), "user_id": str(user_id)},
            }
        )
        
        user_events_json = settings.node.ref.get_all_filtered(query_payload)
        user_events = json.loads(user_events_json) if user_events_json else []
        
        if not user_events:
            raise Exception("Invitation not found")
        
        user_event = user_events[0]
        user_event["status"] = EventStatus.CONFIRMED.value
        
        settings.node.ref.store_key(
            f"user_event:{user_event['id']}", json.dumps(user_event)
        )

    async def decline_invitation(self, event_id: uuid.UUID, user_id: uuid.UUID) -> None:
        # Construir el payload para filtrar la invitación
        query_payload = json.dumps(
            {
                "table": "user_event",
                "filters": {"event_id": str(event_id), "user_id": str(user_id)},
            }
        )
        
        user_events_json = settings.node.ref.get_all_filtered(query_payload)
        user_events = json.loads(user_events_json) if user_events_json else []
        
        if not user_events:
            raise Exception("Invitation not found")
        
        user_event = user_events[0]
        user_event["status"] = EventStatus.CANCELLED.value
        
        settings.node.ref.store_key(
            f"user_event:{user_event['id']}", json.dumps(user_event)
        )

    async def validation_event_in_group(
        self, event_id: uuid.UUID, members: List[UserResponse]
    ) -> None:
        user_events = []
        
        for user in members:
            query_payload = json.dumps(
                {
                    "table": "user_event",
                    "filters": {"event_id": str(event_id), "user_id": str(user.id)},
                }
            )
            ue_json = settings.node.ref.get_all_filtered(query_payload)
            ue_list = json.loads(ue_json) if ue_json else []
            if ue_list:
                user_events.append(ue_list[0])
        
        if not user_events:
            raise Exception("No invitations found for validation")
        
        votes_for = sum(
            1 for ue in user_events if ue["status"] == EventStatus.CONFIRMED.value
        )
        
        votes_against = sum(
            1 for ue in user_events if ue["status"] == EventStatus.CANCELLED.value
        )

        abstentions = len(user_events) - votes_for - votes_against
        validation_result = len(user_events) == votes_for
        
        if not validation_result:
            for ue in user_events:
                settings.node.ref.delete_key(f"user_event:{ue['id']}")
        
        notification_message = (
            f"🎉 The task has been {'validated ✅' if validation_result else 'not validated ❌'}. \n"
            f"🗳️ Voting Summary: \n"
            f"   - Votes For: {votes_for} 👍 \n"
            f"   - Votes Against: {votes_against} 👎 \n"
            f"   - Abstentions: {abstentions} 🤷‍♂️"
        )
        # Enviar una notificación a cada miembro involucrado
        for ue in user_events:
            notification = {
                "id": str(generate_uuid()),
                "recipient": str(ue["user_id"]),
                "sender": str(ue["user_id"]),
                "event": str(event_id),
                "message": notification_message,
                "title": "Info",
                "is_read": False,
                "priority": False,
            }
            settings.node.ref.store_key(
                f"notification:{notification['id']}", json.dumps(notification)
            )
