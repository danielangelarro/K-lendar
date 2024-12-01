from typing import List
import uuid
import inject

from fastapi import APIRouter
from fastapi import Request
from fastapi import HTTPException

from app.api.decorators import require_authentication
from app.domain.models.schemma import GroupCreate, GroupResponse
from app.application.services.group_service import IGroupService

router = APIRouter()


@router.post("/groups/", response_model=GroupResponse)
@require_authentication
async def create_group(group_create: GroupCreate, request: Request):
    group_service: IGroupService = inject.instance(IGroupService)
    group_create.owner = request.state.current_user
    return await group_service.create_group(group_create)


@router.get("/groups/all", response_model=List[GroupResponse])
@require_authentication
async def get_group_all(request: Request):
    group_service: IGroupService = inject.instance(IGroupService)
    
    current_user = request.state.current_user
    group = await group_service.get_group_all(current_user)
    
    return group


@router.get("/groups/{group_id}", response_model=GroupResponse)
@require_authentication
async def get_group(group_id: uuid.UUID, request: Request):
    group_service: IGroupService = inject.instance(IGroupService)
    group = await group_service.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@router.put("/groups/{group_id}", response_model=GroupResponse)
@require_authentication
async def update_group(group_id: uuid.UUID, group_update: GroupCreate, request: Request):
    group_service: IGroupService = inject.instance(IGroupService)

    group_update.owner = request.state.current_user
    updated_group = await group_service.update_group(group_id, group_update)
    
    if not updated_group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    return updated_group


@router.put("/groups/parent/{group_id}/{parent_id}", response_model=GroupResponse)
@require_authentication
async def update_group_parent(group_id: uuid.UUID, parent_id: uuid.UUID, request: Request):
    group_service: IGroupService = inject.instance(IGroupService)

    updated_group = await group_service.update_group_parent(group_id, parent_id)
    
    if not updated_group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    return updated_group


@router.delete("/groups/{group_id}")
@require_authentication
async def delete_group(group_id: uuid.UUID, request: Request):
    group_service: IGroupService = inject.instance(IGroupService)

    user_id = request.state.current_user.id
    await group_service.delete_group(group_id, user_id)
    return {"detail": "Group deleted successfully"}
