import uuid
import inject
from fastapi import APIRouter, HTTPException
from app.application.services.member_service import IMemberService

router = APIRouter()


@router.post("/groups/{group_id}/add_member", response_model=dict)
async def add_member_to_group(group_id: uuid.UUID, user_id: uuid.UUID):
    member_service: IMemberService = inject.instance(IMemberService)

    success = await member_service.add_member(group_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Group or User not found")
    return {"detail": "Member added successfully"}


@router.delete("/groups/{group_id}/remove_member", response_model=dict)
async def remove_member_from_group(group_id: uuid.UUID, user_id: uuid.UUID):
    member_service: IMemberService = inject.instance(IMemberService)
    
    success = await member_service.remove_member(group_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Group or User not found")
    return {"detail": "Member removed successfully"}
