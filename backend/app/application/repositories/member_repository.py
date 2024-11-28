import uuid
from abc import abstractmethod

from app.application.base_repository import BaseRepository
from app.domain.models.schemma import MemberResponse


class IMemberRepository(BaseRepository):
    @abstractmethod
    async def add_member(self, group_id: uuid.UUID, user_id: uuid.UUID) -> MemberResponse:
        pass

    @abstractmethod
    async def remove_member(self, group_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        pass
