import inject
from typing import List
from pydantic import BaseModel

from fastapi import HTTPException
from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.application.services.auth_service import IAuthService
from app.domain.models.schemma import UserCreate
from app.domain.models.schemma import UserResponse
from app.domain.models.schemma import LoginRequest
from app.domain.models.schemma import UserCreate
from app.domain.models.schemma import Token


router = APIRouter()


@router.post("/auth/signup", response_model=UserResponse)
async def register(user: UserCreate):
    auth_service: IAuthService = inject.instance(IAuthService)
    return await auth_service.register_user(user)


@router.post("/auth/signin", response_model=Token)
async def login(login_request: LoginRequest):
    auth_service: IAuthService = inject.instance(IAuthService)

    user = await auth_service.authenticate_user(login_request)
    access_token = auth_service.create_access_token(data={"sub": user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}
