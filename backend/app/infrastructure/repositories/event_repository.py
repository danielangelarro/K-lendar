import json
from typing import List
import uuid

from app.settings import settings
from fastapi import HTTPException

from app.application.repositories.event_repository import IEventRepository
from app.domain.models.enum import EventStatus
from app.domain.models.schemma import EventCreate, EventResponse
from app.infrastructure.repositories.mapper import EventMapper, GroupMapper


class EventRepository(IEventRepository):
    mapper = EventMapper()
    group_mapper = GroupMapper()

    async def create(self, event_create: EventCreate) -> EventResponse:
        event_dict = self.mapper.to_table(event_create)
        # Almacenar el evento
        settings.node.store_key(f"events:{event_dict['id']}", json.dumps(event_dict))

        # Registrar la relación en la tabla user_event
        user_event = {
            "user_id": str(event_create.creator_id),
            "event_id": event_dict["id"],
            "status": event_create.status,
            "group_id": str(event_create.group_id),
        }
        settings.node.store_key(
            f"user_event:{event_dict['id']}", json.dumps(user_event)
        )

        response = self.mapper.to_entity(event_dict)
        response.status = event_create.status
        return response

    async def asign_event(self, event_id: str, user_id: str, group_id: str) -> None:
        user_event = {
            "user_id": user_id,
            "event_id": event_id,
            "status": EventStatus.PENDING.value,
            "group_id": group_id,
        }

        settings.node.store_key(
            f"user_event:{event_id}_{user_id}", json.dumps(user_event)
        )

        event = settings.node.retrieve_key(f"events:{event_id}")
        group = settings.node.retrieve_key(f"events:{group_id}")

        is_owner = False

        if event and group:
            event_data = json.loads(event)
            group_data = json.loads(group)
            is_owner = event_data.get("creator", "") == group_data.get("owner_id", "")

        # Crear la notificación correspondiente
        notification = {
            "recipient": user_id,
            "sender": user_id,
            "event": event_id,
            "priority": is_owner,
            "title": "Event Invitations",
            "message": f"New event assigned for event {event_id} in group {group_id}.",
        }
        settings.node.store_key(
            f"notification:{uuid.uuid4()}", json.dumps(notification)
        )

    async def get_by_id(self, event_id: uuid.UUID) -> EventResponse:
        event_json = settings.node.retrieve_key(f"events:{event_id}")
        ue_json = settings.node.retrieve_key(f"user_event:{event_id}")

        if not event_json or not ue_json:
            return None
        event = json.loads(event_json)
        ue = json.loads(ue_json)

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
            event_json = settings.node.retrieve_key(f"events:{ue['event_id']}")
            if event_json:
                event = json.loads(event_json)
                event["status"] = ue.get("status")

                group_id = ue.get("group_id")
                if group_id:
                    group_json = settings.node.retrieve_key(f"groups:{group_id}")
                    if group_json:
                        event["group"] = json.loads(group_json)

                events.append(self.mapper.to_entity(event))

        return events

    async def update(
        self, event_id: uuid.UUID, event_data: EventCreate
    ) -> EventResponse:
        event_key = f"events:{event_id}"
        event_json = settings.node.retrieve_key(event_key)
        if not event_json:
            raise HTTPException(status_code=404, detail="Event not found")
        event = json.loads(event_json)
        update_data = event_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if key == "end_time":
                setattr(event, "end_datetime", value.isoformat())
            elif key == "start_time":
                setattr(event, "start_datetime", value.isoformat())
            elif key == "event_type":
                setattr(event, key, value.value)
            else:
                event[key] = value
        
        settings.node.store_key(event_key, json.dumps(event))

        ue_key = f"user_event:{event_id}"
        ue_json = settings.node.retrieve_key(ue_key)
        if ue_json:
            ue = json.loads(ue_json)
            ue["status"] = event_data.status
            settings.node.store_key(ue_key, json.dumps(ue))
        response = self.mapper.to_entity(event)
        response.status = event_data.status

        return response

    async def delete(self, event_id: uuid.UUID):
        settings.node.delete_key(f"events:{event_id}")
        settings.node.delete_key(f"user_event:{event_id}")
