from fastapi import APIRouter, HTTPException
from typing import List
from app.application.services.event_service import IEventService
from app.domain.models.schemma import InviteUserRequest
import inject

router = APIRouter()


@router.post("/events/{event_id}/invite")
async def invite_users(event_id: int, invite_request: InviteUserRequest):
    event_service: IEventService = inject.instance(IEventService)
    await event_service.invite_users(event_id, invite_request.user_ids)
    return {"detail": "Users invited successfully"}


@router.post("/events/{event_id}/accept")
async def accept_invitation(event_id: int, user_id: int):
    event_service: IEventService = inject.instance(IEventService)
    await event_service.accept_invitation(event_id, user_id)
    return {"detail": "Invitation accepted"}


@router.post("/events/{event_id}/decline")
async def decline_invitation(event_id: int, user_id: int):
    event_service: IEventService = inject.instance(IEventService)
    await event_service.decline_invitation(event_id, user_id)
    return {"detail": "Invitation declined"}
