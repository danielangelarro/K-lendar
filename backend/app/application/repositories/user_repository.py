import uuid

from abc import abstractmethod

from app.application.base_repository import BaseRepository
from app.domain.models.schemma import UserCreate


class IUserRepository(BaseRepository):
    @abstractmethod
    async def create(self, user: UserCreate):
        pass

    @abstractmethod
    async def update(self, id: uuid.UUID, user_data: dict):
        pass

    @abstractmethod
    async def get_by_id(self, id: uuid.UUID):
        pass

    @abstractmethod
    async def get_by_username(self, username: str):
        pass

    @abstractmethod
    async def get_all(self):
        pass

    @abstractmethod
    async def delete(self, user: UserCreate):
        pass
