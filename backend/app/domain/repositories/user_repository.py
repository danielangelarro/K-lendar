from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from app.domain.models.user import User

class UserRepository(ABC):
    @abstractmethod
    def create_user(self, db: Session, user: User) -> User:
        pass

    @abstractmethod
    def get_user(self, db: Session, user_id: int) -> User:
        pass
