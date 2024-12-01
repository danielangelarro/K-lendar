from typing import List
import uuid
import inject
from fastapi import APIRouter, HTTPException, Request
from app.api.decorators import require_authentication
from app.application.services.member_service import IMemberService
from app.domain.models.schemma import UserResponse

router = APIRouter()


@router.post("/groups/{group_id}/{email}/add_member", response_model=dict)
@require_authentication
async def add_member_to_group(group_id: uuid.UUID, email: str, request: Request):
    member_service: IMemberService = inject.instance(IMemberService)

    success = await member_service.add_member(group_id, email)
    if not success:
        raise HTTPException(status_code=404, detail="Group or User not found")
    return {"detail": "Member added successfully"}


@router.get("/groups/{group_id}/members", response_model=List[UserResponse])
@require_authentication
async def get_member_from_group(group_id: uuid.UUID, request: Request):
    member_service: IMemberService = inject.instance(IMemberService)

    members = await member_service.get_members(group_id)
    
    return members


@router.delete("/groups/{group_id}/{user_id}/remove_member", response_model=dict)
@require_authentication
async def remove_member_from_group(group_id: uuid.UUID, user_id: uuid.UUID, request: Request):
    member_service: IMemberService = inject.instance(IMemberService)
    
    success = await member_service.remove_member(group_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Group or User not found")
    return {"detail": "Member removed successfully"}
