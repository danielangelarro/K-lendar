import uuid
import inject

from app.application.repositories.user_repository import IUserRepository
from app.application.services.user_service import IUserService
from app.domain.models.schemma import UserCreate


class UserService(IUserService):
    repo_instance: IUserRepository = inject.attr(IUserRepository)
    
    async def create_user(self, user: UserCreate):
        return await self.repo_instance.create(user)

    async def update_user(self, id: uuid.UUID, user_data: dict):
        return await self.repo_instance.update(id, user_data)

    async def get_user(self, id: uuid.UUID):
        return await self.repo_instance.get_by_id(id)

    async def get_all_users(self):
        return await self.repo_instance.get_all()

    async def delete_user(self, id: uuid.UUID):
        user = await self.repo_instance.get_by_id(id)
        if user:
            await self.repo_instance.delete(user)
