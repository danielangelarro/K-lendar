import uuid
from typing import List

from app.application.repositories.notification_repository import INotificationRepository
from app.infrastructure.sqlite.tables import Notification
from sqlalchemy.future import select
from sqlalchemy import update


class NotificationRepository(INotificationRepository):
    async def get_by_recipient(self, recipient_id: uuid.UUID) -> List[Notification]:
        db = await self.get_db()
        result = await db.execute(select(Notification).where(Notification.recipient == str(recipient_id)))
        return result.scalars().all()

    async def mark_as_read(self, notification_ids: List[uuid.UUID]) -> None:
        db = await self.get_db()
        stmt = update(Notification).where(Notification.id.in_(notification_ids)).values(is_read=True)
        await db.execute(stmt)
        await db.commit()
