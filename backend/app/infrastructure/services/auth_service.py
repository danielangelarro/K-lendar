import os
import jwt
from datetime import timedelta
from datetime import datetime
from fastapi import HTTPException
from passlib.context import CryptContext
import inject

from app.application.repositories.user_repository import IUserRepository
from app.application.services.auth_service import IAuthService
from app.domain.models.schemma import UserCreate
from app.domain.models.schemma import UserResponse
from app.domain.models.schemma import LoginRequest
from app.settings import settings


class AuthService(IAuthService):
    repo_instance: IUserRepository = inject.attr(IUserRepository)
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def register_user(self, user: UserCreate) -> UserResponse:
        user.password = self.get_password_hash(user.password)
        return await self.repo_instance.create(user)

    async def authenticate_user(self, login_request: LoginRequest) -> UserResponse:
        user = await self.repo_instance.get_by_id(login_request.username)
        if not user or not self.verify_password(login_request.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        return user

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)
