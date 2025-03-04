from datetime import datetime
import json
from typing import List
import uuid

from app.infrastructure.sqlite.utils import generate_uuid
from app.settings import settings
from fastapi import HTTPException

from app.application.repositories.event_repository import IEventRepository
from app.domain.models.enum import EventStatus, EventType
from app.domain.models.schemma import EventCreate, EventResponse
from app.infrastructure.repositories.mapper import EventMapper, GroupMapper


class EventRepository(IEventRepository):
    mapper = EventMapper()
    group_mapper = GroupMapper()

    async def create(self, event_create: EventCreate) -> EventResponse:
        event_dict = self.mapper.to_table(event_create)
        # Almacenar el evento
        await settings.node.store_key(f"events:{event_dict['id']}", json.dumps(event_dict))

        # Registrar la relación en la tabla user_event
        user_event = {
            "id": generate_uuid(),
            "user_id": str(event_create.creator_id),
            "event_id": event_dict["id"],
            "status": event_create.status,
            "group_id": str(event_create.group_id) if event_create.group_id else None,
        }
        await settings.node.store_key(
            f"user_event:{user_event['id']}", json.dumps(user_event)
        )

        response = self.mapper.to_entity(event_dict)
        response.status = event_create.status
        return response

    async def asign_event(self, event_id: str, user_id: str, group_id: str, status: str) -> None:
        user_event = {
            "id": generate_uuid(),
            "user_id": user_id,
            "event_id": event_id,
            "status": status,
            "group_id": group_id,
        }

        await settings.node.store_key(
            f"user_event:{user_event['id']}", json.dumps(user_event)
        )

        event = await settings.node.retrieve_key(f"events:{event_id}")
        group = await settings.node.retrieve_key(f"events:{group_id}")

        is_owner = False

        if event and group:
            event_data = json.loads(event)
            group_data = json.loads(group)
            is_owner = event_data.get("creator", "") == group_data.get("owner_id", "")

        # Crear la notificación correspondiente
        notification = {
            "id": generate_uuid(),
            "recipient": user_id,
            "sender": user_id,
            "event": event_id,
            "priority": is_owner,
            "title": "Event Invitations",
            "message": f"New event assigned for event {event_id} in group {group_id}.",
        }
        await settings.node.store_key(
            f"notification:{notification['id']}", json.dumps(notification)
        )

    async def get_by_id(self, event_id: uuid.UUID) -> EventResponse:
        event_json = await settings.node.retrieve_key(f"events:{event_id}")

        query_payload = json.dumps(
            {"table": "user_event", "filters": {"event_id": str(event_id)}}
        )
        ue_json = settings.node.ref.get_all_filtered(query_payload)
        ue_list = json.loads(ue_json) if ue_json else []
        
        if not event_json or not ue_list:
            return None
        event = json.loads(event_json)
        ue = ue_list[0]

        response = self.mapper.to_entity(event)
        response.status = ue.get("status")

        return response

    async def get_by_user_id(self, user_id: uuid.UUID) -> List[EventResponse]:
        query_payload = json.dumps(
            {"table": "user_event", "filters": {"user_id": str(user_id)}}
        )
        user_events_json = settings.node.ref.get_all_filtered(query_payload)
        user_events = json.loads(user_events_json) if user_events_json else []

        events = []
        for ue in user_events:
            event_json = await settings.node.retrieve_key(f"events:{ue['event_id']}")
            if event_json:
                event = json.loads(event_json)
                event["status"] = ue.get("status", "personal")

                group_id = ue.get("group_id")
                if group_id:
                    group_json = await settings.node.retrieve_key(f"groups:{group_id}")
                    if group_json:
                        event["group"] = json.loads(group_json)

                events.append(self.mapper.to_entity(event))

        return events

    async def update(
        self, event_id: uuid.UUID, event_data: EventCreate
    ) -> EventResponse:
        event_key = f"events:{event_id}"
        event_json = await settings.node.retrieve_key(event_key)

        if not event_json:
            raise HTTPException(status_code=404, detail="Event not found")
        
        event = json.loads(event_json)
        update_data = event_data.dict(exclude_unset=True)
        
        event_updated = {
            "id": event_id,
            "title": update_data['title'],
            "description": update_data['description'],
            "start_datetime": update_data['start_time'].isoformat(),  # Datetime a string ISO
            "end_datetime": update_data['end_time'].isoformat(),
            "event_type": update_data['event_type'].value,
            "creator": event['creator']
        }

        await settings.node.store_key(event_key, json.dumps(event_updated))

        query_payload = json.dumps({"table": "user_event", "filters": {"event_id": event_id}})
        user_events_json = settings.node.ref.get_all_filtered(query_payload)
        user_events = json.loads(user_events_json) if user_events_json else []

        for user_event in user_events:
            ue_key = f"user_event:{user_event['id']}"
            print(f"~~~ event_repository ~ update [user_event]: {user_event}")

            user_event_updated = user_event.copy()
            user_event_updated["status"] = update_data['status']
            
            print(f"~~~ event_repository ~ update [user_event_updated]: {user_event_updated}")

            await settings.node.store_key(ue_key, json.dumps(user_event_updated))
        
        response = self.mapper.to_entity(event)
        response.status = event_data.status

        return response

    async def delete(self, event_id: uuid.UUID):
        await settings.node.delete_key(f"events:{event_id}")
        await settings.node.delete_key(f"user_event:{event_id}")
