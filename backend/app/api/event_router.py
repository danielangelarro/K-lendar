from fastapi import APIRouter
from fastapi import Request
from fastapi import HTTPException
from app.api.decorators import require_authentication
from app.application.services.event_service import IEventService
from app.domain.models.schemma import EventCreate, EventResponse
import inject

router = APIRouter()


@router.post("/events/", response_model=EventResponse)
@require_authentication
async def create_event(event_create: EventCreate, request: Request):
    event_service: IEventService = inject.instance(IEventService)

    current_user = request.state.current_user
    event_create.creator_id = current_user.id

    return await event_service.create_event(event_create)


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
async def update_event(event_id: int, event_update: EventCreate, request: Request):
    event_service: IEventService = inject.instance(IEventService)
    updated_event = await event_service.update_event(event_id, event_update)
    if not updated_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated_event


@router.delete("/events/{event_id}", response_model=dict)
@require_authentication
async def delete_event(event_id: int, request: Request):
    event_service: IEventService = inject.instance(IEventService)
    await event_service.delete_event(event_id)
    return {"detail": "Event deleted successfully"}
