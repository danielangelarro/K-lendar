from app.application.base_repository import BaseMapper
from app.domain.models.schemma import UserCreate
from app.domain.models.schemma import UserResponse
from app.infrastructure.postgresql.tables import User


class UserMapper(BaseMapper):
    def to_table(user_create: UserCreate) -> User:
        return User(
            username=user_create.username,
            email=user_create.email,
            password=user_create.password,
            role=user_create.role
        )

    def to_entity(user: User) -> UserResponse:
        return UserResponse(
            username=user.username,
            email=user.email,
            role=user.role
        )
