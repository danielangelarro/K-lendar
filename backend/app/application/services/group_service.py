import uuid

from abc import ABC, abstractmethod
from app.application.base_repository import BaseRepository
from app.domain.models.schemma import GroupCreate
from app.domain.models.schemma import GroupResponse


class IGroupService(ABC):
    repo_instance: BaseRepository = None

    @abstractmethod
    async def create_group(self, group: GroupCreate) -> GroupResponse:
        pass

    @abstractmethod
    async def get_group(self, group_id: int) -> GroupResponse:
        pass

    @abstractmethod
    async def update_group(self, group_id: int, group_data: GroupCreate) -> GroupResponse:
        pass

    @abstractmethod
    async def delete_group(self, group_id: int):
        pass
