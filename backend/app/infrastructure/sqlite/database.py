from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.infrastructure.sqlite.tables import Base


def get_engine():
    from app.settings import settings  # Import inside the function
    return create_async_engine(settings.DATABASE_URL, echo=True)

@asynccontextmanager
async def get_db():
    engine = get_engine()
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
