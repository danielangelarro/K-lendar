import uuid
from abc import ABC, abstractmethod
from app.domain.models.schemma import UserCreate
from app.domain.models.schemma import UserResponse
from app.domain.models.enum import UserRole
from app.domain.models.schemma import LoginRequest


class IAuthService(ABC):
    @abstractmethod
    async def register_user(self, user: UserCreate) -> UserResponse:
        pass

    @abstractmethod
    async def authenticate_user(self, login_request: LoginRequest) -> UserResponse:
        pass

    @abstractmethod
    def create_access_token(self, data: dict) -> str:
        pass
