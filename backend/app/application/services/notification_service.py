import uuid

from typing import List
from abc import ABC, abstractmethod

from app.domain.models.schemma import NotificationResponse
from app.application.base_repository import BaseRepository


class INotificationService(ABC):
    repo_instance: BaseRepository = None

    @abstractmethod
    async def get_notifications(self, user_id: uuid.UUID) -> List[NotificationResponse]:
        pass

    @abstractmethod
    async def mark_as_read(self, notification_ids: List[uuid.UUID]) -> None:
        pass
