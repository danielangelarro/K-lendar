import uuid
import inject
from fastapi import APIRouter, Request

from app.api.decorators import require_authentication
from app.application.services.event_service import IEventService
from app.domain.models.schemma import InviteUserRequest


router = APIRouter()


@router.post("/events/{event_id}/invite")
@require_authentication
async def invite_users(event_id: uuid.UUID, invite_request: InviteUserRequest, request: Request):
    event_service: IEventService = inject.instance(IEventService)
    await event_service.invite_users(event_id, invite_request.user_ids)
    return {"detail": "Users invited successfully"}


@router.post("/events/{event_id}/accept")
@require_authentication
async def accept_invitation(event_id: uuid.UUID, request: Request):
    event_service: IEventService = inject.instance(IEventService)
    
    current_user = request.state.current_user
    await event_service.accept_invitation(event_id, current_user.id)
    
    return {"detail": "Invitation accepted"}


@router.post("/events/{event_id}/decline")
@require_authentication
async def decline_invitation(event_id: uuid.UUID, request: Request):
    event_service: IEventService = inject.instance(IEventService)
    
    current_user = request.state.current_user
    await event_service.decline_invitation(event_id, current_user.id)

    return {"detail": "Invitation declined"}
