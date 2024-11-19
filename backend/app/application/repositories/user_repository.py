import uuid

from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.schemma import UserCreate


class IUserRepository(ABC):
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
    async def get_all(self):
        pass

    @abstractmethod
    async def delete(self, user: UserCreate):
        pass
