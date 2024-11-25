from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.settings import settings
from app.infrastructure.sqlite.tables import Base


engine = create_async_engine(settings.DATABASE_URL, echo=True)


async def get_db():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
