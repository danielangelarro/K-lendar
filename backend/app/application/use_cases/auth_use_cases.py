from sqlalchemy.orm import Session
from app.api.schemas.user import UserCreate, UserLogin
from app.infrastructure.repositories import user_repository
from app.infrastructure.security import verify_password

def register_user(db: Session, user: UserCreate):
    if user_repository.get_user_by_username(db, user.username) or user_repository.get_user_by_email(db, user.email):
        raise ValueError("Username or email already registered")
    return user_repository.create_user(db, user)

def authenticate_user(db: Session, user: UserLogin):
    db_user = user_repository.get_user_by_username(db, user.username)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        return None
    return db_user
