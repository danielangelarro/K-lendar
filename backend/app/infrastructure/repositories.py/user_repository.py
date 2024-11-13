from sqlalchemy.orm import Session
from app.domain.models.user import User
from app.domain.repositories.user_repository import UserRepository

class UserRepositoryImpl(UserRepository):
    def create_user(self, db: Session, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_user(self, db: Session, user_id: int) -> User:
        return db.query(User).filter(User.id == user_id).first()
