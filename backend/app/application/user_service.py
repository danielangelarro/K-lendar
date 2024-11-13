from sqlalchemy.orm import Session
from app.domain.models.user import User
from app.domain.repositories.user_repository import UserRepository

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, db: Session, name: str, email: str) -> User:
        user = User(name=name, email=email)
        return self.user_repository.create_user(db, user)

    def get_user(self, db: Session, user_id: int) -> User:
        return self.user_repository.get_user(db, user_id)
