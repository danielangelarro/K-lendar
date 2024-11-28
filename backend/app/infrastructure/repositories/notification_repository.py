import uuid
from typing import List

from app.application.repositories.notification_repository import INotificationRepository
from app.domain.models.schemma import NotificationResponse
from app.infrastructure.repositories.mapper import NotificationMapper
from app.infrastructure.sqlite.tables import Notification
from sqlalchemy.future import select
from sqlalchemy import update


class NotificationRepository(INotificationRepository):
    mapper = NotificationMapper()

    async def get_by_recipient(self, recipient_id: uuid.UUID) -> List[NotificationResponse]:
        db = await self.get_db()
        result = await db.execute(select(Notification).where(Notification.recipient == str(recipient_id)))
        notifications = result.scalars().all()
        return [self.mapper.to_entity(notification) for notification in notifications]

    async def mark_as_read(self, notification_id: uuid.UUID) -> None:
        db = await self.get_db()
        notification = await db.execute(select(Notification).where(Notification.id == str(notification_id)))
        notification = notification.scalars().first()
        if notification:
            notification.is_read = True
            await db.commit()
        else:
            raise Exception("Notification not found")
