from typing import List
import uuid

from abc import abstractmethod
from app.application.base_repository import BaseRepository
from app.domain.models.schemma import GroupCreate, UserResponse
from app.domain.models.schemma import GroupResponse


class IGroupRepository(BaseRepository):
    @abstractmethod
    async def create(self, group_create: GroupCreate) -> GroupResponse:
        pass

    @abstractmethod
    async def get_by_id(self, group_id: uuid.UUID) -> GroupResponse:
        pass

    @abstractmethod
    async def get_by_user(self, user: UserResponse) -> List[GroupResponse]:
        pass

    @abstractmethod
    async def get_by_name(self, group_id: uuid.UUID) -> GroupResponse:
        pass

    @abstractmethod
    async def update(self, group_id: uuid.UUID, group_data: GroupCreate) -> GroupResponse:
        pass

    @abstractmethod
    async def update_parent(self, group_id: uuid.UUID, parent_group_id: uuid.UUID):
        pass

    @abstractmethod
    async def delete(self, group_id: uuid.UUID, user_id: uuid.UUID):
        pass

    @abstractmethod
    async def set_parent_group(self, group_id: uuid.UUID, parent_group_id: uuid.UUID):
        pass
