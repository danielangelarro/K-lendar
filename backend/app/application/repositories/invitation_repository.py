from typing import List
import uuid

from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.schemma import UserCreate


class IInvitationRepository(ABC):
    @abstractmethod
    async def invite_users(self, event_id: uuid.UUID, user_ids: List[uuid.UUID]) -> None:
        pass

    @abstractmethod
    async def accept_invitation(self, event_id: uuid.UUID, user_id: uuid.UUID) -> None:
        pass

    @abstractmethod
    async def decline_invitation(self, event_id: uuid.UUID, user_id: uuid.UUID) -> None:
        pass
