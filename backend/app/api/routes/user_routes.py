from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.db.session import SessionLocal
from app.application.user_service import UserService
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from app.domain.models.user import User

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

user_service = UserService(UserRepositoryImpl())

@router.post("/users/", response_model=User)
def create_user(name: str, email: str, db: Session = Depends(get_db)):
    return user_service.create_user(db, name, email)

@router.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = user_service.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
