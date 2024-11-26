from fastapi import APIRouter, HTTPException
from typing import List
from app.application.services.event_service import IEventService
from app.domain.models.schemma import EventCreate, EventResponse
import inject

router = APIRouter()

@router.post("/events/", response_model=EventResponse)
async def create_event(event_create: EventCreate):
    event_service: IEventService = inject.instance(IEventService)
    return await event_service.create_event(event_create)

@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(event_id: int):
    event_service: IEventService = inject.instance(IEventService)
    event = await event_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.put("/events/{event_id}", response_model=EventResponse)
async def update_event(event_id: int, event_update: EventCreate):
    event_service: IEventService = inject.instance(IEventService)
    updated_event = await event_service.update_event(event_id, event_update)
    if not updated_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated_event

@router.delete("/events/{event_id}", response_model=dict)
async def delete_event(event_id: int):
    event_service: IEventService = inject.instance(IEventService)
    await event_service.delete_event(event_id)
    return {"detail": "Event deleted successfully"}
