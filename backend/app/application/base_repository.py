from abc import ABC
from abc import abstractmethod
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.sqlite.database import get_db


class BaseMapper(ABC):
    @abstractmethod
    def to_entity(self, data):
        pass

    @abstractmethod
    def to_table(self, entity):
        pass


class BaseRepository(ABC):
    db_instance: AsyncSession = None
    mapper: Optional[BaseMapper] = None
    
    async def get_db(cls):
        if cls.db_instance is None:
            async_generator = get_db()
            cls.db_instance = await async_generator.__anext__() 
        return cls.db_instance

    async def commit(self):
        db = await self.get_db()
        await db.commit()

    async def refresh(self, instance):
        db = await self.get_db()
        await db.refresh(instance)
