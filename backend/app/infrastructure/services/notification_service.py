import uuid
from typing import List
import inject
from app.application.services.notification_service import INotificationService
from app.application.repositories.notification_repository import INotificationRepository
from app.domain.models.schemma import NotificationResponse


class NotificationService(INotificationService):
    repo_instance: INotificationRepository = inject.attr(INotificationRepository)

    async def get_notifications(self, user_id: uuid.UUID) -> List[NotificationResponse]:
        return await self.repo_instance.get_by_recipient(user_id)

    async def mark_as_read(self, notification_ids: List[uuid.UUID]) -> None:
        await self.repo_instance.mark_as_read(notification_ids)
