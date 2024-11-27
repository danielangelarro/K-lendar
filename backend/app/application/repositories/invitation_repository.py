import uuid
from typing import List

from abc import abstractmethod

from app.application.base_repository import BaseRepository


class IInvitationRepository(BaseRepository):
    @abstractmethod
    async def invite_users(self, event_id: uuid.UUID, user_ids: List[uuid.UUID]) -> None:
        pass

    @abstractmethod
    async def accept_invitation(self, event_id: uuid.UUID, user_id: uuid.UUID) -> None:
        pass

    @abstractmethod
    async def decline_invitation(self, event_id: uuid.UUID, user_id: uuid.UUID) -> None:
        pass
