import uuid
from typing import List

from abc import ABC, abstractmethod
from app.application.base_repository import BaseRepository


class IMemberService(ABC):
    repo_instance: BaseRepository = None

    @abstractmethod
    async def add_member(self, group_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        pass

    @abstractmethod
    async def remove_member(self, group_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        pass

