import json
import logging
import uuid

from app.settings import settings
from app.application.repositories.user_repository import IUserRepository
from app.domain.models.schemma import UserCreate
from app.domain.models.schemma import UserResponse
from app.infrastructure.repositories.mapper import UserMapper


class UserRepository(IUserRepository):
    mapper = UserMapper()

    async def create(self, user_create: UserCreate) -> UserResponse:
        user = self.mapper.to_table(user_create)
        
        settings.node.ref.store_key(f"users:{user['id']}", json.dumps(user))

        return self.mapper.to_entity(user)

    async def update(self, id: uuid.UUID, user_data: dict) -> UserResponse:
        user_key = f"users:{id}"
        user_json = settings.node.ref.retrieve_key(user_key)

        if not user_json:
            raise Exception("User not found")
        user = json.loads(user_json)

        for key, value in user_data.items():
            user[key] = value
        settings.node.ref.store_key(user_key, json.dumps(user))

        return self.mapper.to_entity(user)

    async def get_by_id(self, id: uuid.UUID) -> UserResponse:
        user_json = settings.node.ref.retrieve_key(f"users:{id}")
        if user_json:
            user = json.loads(user_json)
            return self.mapper.to_entity(user)
        return None

    async def get_by_username(self, username: str) -> UserResponse:
        payload = {
            "table": "users",
            "filters": {"username": username}
        }
        users_json = settings.node.ref.get_all_filtered(json.dumps(payload))
        users_list = json.loads(users_json) if users_json else []

        print("user_list", users_list)

        if not users_list:
            return None

        return self.mapper.to_entity(users_list[0])

    async def get_all(self) -> list[UserResponse]:
        payload = {
            "table": "users",
            "filters": {}
        }
        users_json = settings.node.ref.get_all_filtered(json.dumps(payload))
        users = json.loads(users_json) if users_json else []

        return [self.mapper.to_entity(user) for user in users]

    async def delete(self, id: uuid.UUID):
        user_key = f"users:{id}"
        user_json = settings.node.ref.retrieve_key(user_key)

        if user_json:
            settings.node.ref.delete_key(user_key)
