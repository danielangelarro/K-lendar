import uuid
import inject

from typing import List
from fastapi import APIRouter
from fastapi import Request
from fastapi import HTTPException
from app.api.decorators import require_authentication
from app.domain.models.enum import EventType
from app.application.services.event_service import IEventService
from app.application.services.group_service import IGroupService
from app.domain.models.schemma import EventCreate, EventRequest, EventResponse

router = APIRouter()


@router.post("/events/create/", response_model=EventResponse)
@require_authentication
async def create_event(event_request: EventRequest, request: Request):
    group_service: IGroupService = inject.instance(IGroupService)
    event_service: IEventService = inject.instance(IEventService)
    group = None

    if event_request.group_name:
        group = await group_service.get_group_by_name(event_request.group_name)

        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

    current_user = request.state.current_user

    event_create = EventCreate(
        title=event_request.title,
        description=event_request.description,
        status=event_request.status,
        start_time=event_request.start_time,
        end_time=event_request.end_time,
        event_type=event_request.event_type,
        creator_id=current_user.id,
        group_id=group.id if group else None,
        invitees=[]
    )

    response = None

    match event_request.event_type:
        case EventType.PERSONAL:
            response = await event_service.create_event(event_create)
            pass
        case EventType.GROUP:
            response = await event_service.create_event_group(event_create)
            pass
        case EventType.HIERARCHICAL:
            response = await event_service.create_event_hierarchical(event_create)
            pass

    return response


@router.get("/events/", response_model=List[EventResponse])
@require_authentication
async def get_all_event(request: Request):
    event_service: IEventService = inject.instance(IEventService)
    
    current_user = request.state.current_user
    events = await event_service.get_all_event(current_user.id)
    
    return events


@router.get("/events/{event_id}", response_model=EventResponse)
@require_authentication
async def get_event(event_id: int, request: Request):
    event_service: IEventService = inject.instance(IEventService)
    event = await event_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.put("/events/{event_id}", response_model=EventResponse)
@require_authentication
async def update_event(event_id: str, event_request: EventRequest, request: Request):
    group_service: IGroupService = inject.instance(IGroupService)
    event_service: IEventService = inject.instance(IEventService)
    group = None

    if event_request.group_name:
        group = group_service.get_group_by_name(event_request.group_name)

        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

    current_user = request.state.current_user

    event_update = EventCreate(
        title=event_request.title,
        description=event_request.description,
        status=event_request.status,
        start_time=event_request.start_time,
        end_time=event_request.end_time,
        event_type=event_request.event_type,
        creator_id=current_user.id,
        group_id=group.id if group else None,
        invitees=[]
    )

    updated_event = await event_service.update_event(event_id, event_update)
    if not updated_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated_event


@router.delete("/events/{event_id}", response_model=dict)
@require_authentication
async def delete_event(event_id: str, request: Request):
    event_service: IEventService = inject.instance(IEventService)
    await event_service.delete_event(event_id)
    return {"detail": "Event deleted successfully"}
