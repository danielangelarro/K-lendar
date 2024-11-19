from fastapi import HTTPException
from fastapi import APIRouter
from fastapi import Depends
import inject

from app.application.services.user_service import IUserService
from app.domain.models.schemma import UserCreate
from app.domain.models.enum import UserRole

from pydantic import BaseModel
from typing import List


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserUpdate(BaseModel):
    name: str = None
    email: str = None
    password: str = None
    role: UserRole = None


router = APIRouter()

@router.post("/users/", response_model=UserCreate )
async def create_user(user_create: UserCreate):
    user_service: IUserService = inject.instance(IUserService)
    
    user = UserCreate(**user_create.dict())
    return await user_service.create_user(user)


@router.put("/users/{id}", response_model=UserCreate )
async def update_user(id: int, user_update: UserUpdate):
    user_service: IUserService = inject.instance(IUserService)
    
    user_data = user_update.dict(exclude_unset=True)
    updated_user = await user_service.update_user(id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User  not found")
    return updated_user


@router.get("/users/{id}", response_model=UserCreate )
async def get_user(id: int):
    user_service: IUserService = inject.instance(IUserService)
    
    user = await user_service.get_user(id)
    if not user:
        raise HTTPException(status_code=404, detail="User  not found")
    return user


@router.get("/users/", response_model=List[UserCreate ])
async def get_all_users():
    user_service: IUserService = inject.instance(IUserService)
    
    return await user_service.get_all_users()


@router.delete("/users/{id}", response_model=dict)
async def delete_user(id: int):
    user_service: IUserService = inject.instance(IUserService)
    
    await user_service.delete_user(id)
    return {"detail": "User  deleted successfully"}
