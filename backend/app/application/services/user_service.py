import uuid

from abc import ABC, abstractmethod
from app.application.base_repository import BaseRepository
from app.domain.models.schemma import UserCreate


class IUserService(ABC):
    repo_instance: BaseRepository = None

    @abstractmethod
    async def create_user(self, user: UserCreate):
        pass

    @abstractmethod
    async def update_user(self, id: uuid.UUID, user_data: dict):
        pass

    @abstractmethod
    async def get_user(self, id: uuid.UUID):
        pass

    @abstractmethod
    async def get_all_users(self):
        pass

    @abstractmethod
    async def delete_user(self, id: uuid.UUID):
        pass
