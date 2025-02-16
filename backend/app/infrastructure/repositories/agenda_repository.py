import json
import uuid
from typing import List
from datetime import datetime

from app.settings import settings
from app.domain.models.schemma import UserAgendaResponse
from app.application.repositories.agenda_repository import IAgendaRepository
from app.infrastructure.repositories.mapper import EventMapper, GroupMapper


class AgendaRepository(IAgendaRepository):
    mapper = EventMapper()
    group_mapper = GroupMapper()

    async def get_user_agenda(
        self, user_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> UserAgendaResponse:
        # Recuperar la información del usuario desde el anillo
        user_json = await settings.node.retrieve_key(f"users:{user_id}")
        if not user_json:
            raise Exception("Usuario no encontrado")
        user = json.loads(user_json)

        # Construir el payload de la consulta filtrada en la tabla de eventos
        query_payload = json.dumps(
            {
                "table": "events",
                "filters": {
                    "start_datetime": {"gte": start_date.isoformat()},
                    "end_datetime": {"lte": end_date.isoformat()},
                    "creator": str(user_id),
                },
            }
        )
        events_json = settings.node.ref.get_all_filtered(query_payload)
        events_list = json.loads(events_json) if events_json else []
        events = []
        for ev in events_list:
            # Recuperar el estado del evento (se asume que se almacena bajo "user_event:<event_id>")
            ue_json = await settings.node.retrieve_key(f"user_event:{ev['id']}")
            if ue_json:
                ue = json.loads(ue_json)
                ev["status"] = ue.get("status")
                group_id = ue.get("group_id")
                if group_id:
                    group_json = await settings.node.retrieve_key(f"groups:{group_id}")
                    if group_json:
                        ev["group"] = json.loads(group_json)
            # Convertir el diccionario a entidad usando el mapper
            event_entity = self.mapper.to_entity(ev)
            events.append(event_entity)

        return UserAgendaResponse(user_id=user_id, name=user["username"], events=events)

    async def get_group_agenda(
        self, group_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> List[UserAgendaResponse]:
        # Se consulta la tabla "member" para obtener los miembros del grupo
        query_payload = json.dumps(
            {"table": "member", "filters": {"group_id": str(group_id)}}
        )
        members_json = settings.node.ref.get_all_filtered(query_payload)
        members_list = json.loads(members_json) if members_json else []
        member_ids = [m["user_id"] for m in members_list]

        responses = []
        for mem_id in member_ids:
            agenda = await self.get_user_agenda(uuid.UUID(mem_id), start_date, end_date)
            responses.append(agenda)
        return responses
