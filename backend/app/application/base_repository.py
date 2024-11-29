from abc import ABC
from abc import abstractmethod
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession


class BaseMapper(ABC):
    @abstractmethod
    def to_entity(self, data):
        pass

    @abstractmethod
    def to_table(self, entity):
        pass


class BaseRepository(ABC):
    mapper: Optional[BaseMapper] = None
    
    async def commit(self, db: AsyncSession):
        await db.commit()

    async def refresh(self, db: AsyncSession, instance):
        await db.refresh(instance)
