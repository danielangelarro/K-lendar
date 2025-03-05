import json
import uuid
from typing import List
from app.application.repositories.notification_repository import INotificationRepository
from app.domain.models.schemma import NotificationResponse
from app.infrastructure.repositories.mapper import NotificationMapper
from app.settings import settings


class NotificationRepository(INotificationRepository):
    mapper = NotificationMapper()

    async def get_by_recipient(
        self, recipient_id: uuid.UUID
    ) -> List[NotificationResponse]:
        # Construir el payload para filtrar la tabla "notification" por recipient e is_read=False
        payload = {
            "table": "notification",
            "filters": {"recipient": str(recipient_id), "is_read": False},
        }
        notifications_json = settings.node.ref.get_all_filtered(json.dumps(payload))
        notifications_list = (
            json.loads(notifications_json) if notifications_json else []
        )
        # Convertir cada registro a entidad usando el mapper
        return [self.mapper.to_entity(n) for n in notifications_list]

    async def mark_as_read(self, notification_ids: List[uuid.UUID]) -> None:
        for notif_id in notification_ids:
            key = f"notification:{notif_id}"
            notif_json = settings.node.ref.retrieve_key(key)
            if notif_json:
                notif = json.loads(notif_json)
                notif["is_read"] = True
                settings.node.ref.store_key(key, json.dumps(notif))
            else:
                raise Exception("Notification not found")
