import os
import inject
from pydantic import BaseSettings


def configure(binder):
    from app.infrastructure.repositories.user_repository import UserRepository
    from app.infrastructure.services.user_service import UserService
    from app.application.repositories.user_repository import IUserRepository
    from app.application.services.user_service import IUserService

    binder.bind(IUserRepository, UserRepository())
    binder.bind(IUserService, UserService())


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:root@localhost:5432/kcalendar")

    class Config:
        env_file = ".env"


settings = Settings()
