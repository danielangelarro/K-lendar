import uuid

from app.application.repositories.user_repository import IUserRepository
from app.domain.models.schemma import UserCreate
from app.domain.models.schemma import UserResponse
from app.infrastructure.sqlite.tables import User
from app.infrastructure.sqlite.database import get_db
from app.infrastructure.repositories.mapper import UserMapper


from sqlalchemy.future import select


class UserRepository(IUserRepository):
    mapper = UserMapper()

    async def create(self, user_create: UserCreate) -> UserResponse:
        async with get_db() as db:
            user = self.mapper.to_table(user_create)
            db.add(user)
            try:
                await self.commit(db)
                await self.refresh(db, user)
                return self.mapper.to_entity(user)
            except Exception as e:
                await db.rollback()
                raise e

    async def update(self, id: uuid.UUID, user_data: dict) -> UserResponse:
        async with get_db() as db:
            user = await self.get_by_id(str(id))
            for key, value in user_data.items():
                setattr(user, key, value)
            
            try:
                await self.commit(db)
                await self.refresh(db, user)
                return self.mapper.to_entity(user)
            except Exception as e:
                await db.rollback()
                raise e

    async def get_by_id(self, id: uuid.UUID) -> UserResponse:
        async with get_db() as db:
            result = await db.execute(select(User).where(User.id == str(id)))
            user = result.scalars().first()
            return self.mapper.to_entity(user) if user else None

    async def get_by_username(self, username: str) -> UserResponse:
        async with get_db() as db:
            result = await db.execute(select(User).where(User.username == username))
            user = result.scalars().first()
            return self.mapper.to_entity(user) if user else None


    async def get_all(self) -> list[UserResponse]:
        async with get_db() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
            return [self.mapper.to_entity(user) for user in users]

    async def delete(self, id: uuid.UUID):
        async with get_db() as db:
            user = await self.get_by_id(str(id))
            if user:
                try:
                    await db.delete(db, user)
                    await self.commit(db)
                except Exception as e:
                    await db.rollback()
                    raise e
