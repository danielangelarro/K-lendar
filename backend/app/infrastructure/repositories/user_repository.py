import uuid

from app.application.repositories.user_repository import IUserRepository
from app.application.base_repository import BaseRepository
from app.domain.models.schemma import UserCreate
from app.domain.models.schemma import UserResponse
from app.infrastructure.postgresql.tables import User
from app.infrastructure.repositories.mapper import UserMapper


from sqlalchemy.future import select


class UserRepository(BaseRepository, IUserRepository):
    mapper = UserMapper()

    async def create(self, user_create: UserCreate) -> UserResponse:
        db = await self.get_db()
        user = self.mapper.to_table(user_create)  # Mapeo de esquema a modelo
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return self.mapper.to_entity(user)  # Mapeo de modelo a esquema de respuesta

    async def update(self, id: uuid.UUID, user_data: dict) -> UserResponse:
        db = await self.get_db()
        user = await self.get_by_id(id)
        for key, value in user_data.items():
            setattr(user, key, value)
        await db.commit()
        await db.refresh(user)
        return self.mapper.to_entity(user)  # Mapeo de modelo a esquema de respuesta

    async def get_by_id(self, id: uuid.UUID) -> UserResponse:
        db = await self.get_db()
        result = await db.execute(select(User).where(User.id == str(id)))  # Asegúrate de usar el modelo correcto
        user = result.scalars().first()
        return self.mapper.to_entity(user) if user else None  # Mapeo de modelo a esquema de respuesta

    async def get_all(self) -> list[UserResponse]:
        db = await self.get_db()
        result = await db.execute(select(User))
        users = result.scalars().all()
        return [self.mapper.to_entity(user) for user in users]  # Mapeo de modelos a esquemas de respuesta

    async def delete(self, id: uuid.UUID):
        db = await self.get_db()
        user = await self.get_by_id(id)
        if user:
            await db.delete(user)
            await db.commit()
