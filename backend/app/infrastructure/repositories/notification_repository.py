import uuid
from typing import List

from app.application.repositories.notification_repository import INotificationRepository
from app.domain.models.schemma import NotificationResponse
from app.infrastructure.repositories.mapper import NotificationMapper
from app.infrastructure.sqlite.tables import Notification
from app.infrastructure.sqlite.database import get_db
from sqlalchemy.future import select
from sqlalchemy import update


class NotificationRepository(INotificationRepository):
    mapper = NotificationMapper()

    async def get_by_recipient(self, recipient_id: uuid.UUID) -> List[NotificationResponse]:
        async with get_db() as db:
            result = await db.execute(select(Notification).where(Notification.recipient == str(recipient_id)))
            notifications = result.scalars().all()
            return [self.mapper.to_entity(notification) for notification in notifications]

    async def mark_as_read(self, notification_id: uuid.UUID) -> None:
        async with get_db() as db:
            notification = await db.execute(select(Notification).where(Notification.id == str(notification_id)))
            notification = notification.scalars().first()
            if notification:
                notification.is_read = True
                
                try:
                    await self.commit(db)
                except Exception as e:
                    await db.rollback()
                    raise e
            else:
                raise Exception("Notification not found")
