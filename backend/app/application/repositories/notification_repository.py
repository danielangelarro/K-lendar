import uuid
from typing import List
from abc import abstractmethod

from app.application.base_repository import BaseRepository
from app.infrastructure.sqlite.tables import Notification


class INotificationRepository(BaseRepository):
    @abstractmethod
    async def get_by_recipient(self, recipient_id: uuid.UUID) -> List[Notification]:
        pass

    @abstractmethod
    async def mark_as_read(self, notification_ids: List[uuid.UUID]) -> None:
        pass
