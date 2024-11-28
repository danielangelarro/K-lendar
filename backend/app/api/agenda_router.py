import uuid
from datetime import datetime
import inject
from fastapi import APIRouter, Request, HTTPException
from app.api.decorators import require_authentication
from app.application.services.agenda_service import IAgendaService
from app.domain.models.schemma import UserAgendaResponse

router = APIRouter()


@router.get("/agendas/{user_id}", response_model=UserAgendaResponse)
@require_authentication
async def get_user_agenda(user_id: uuid.UUID, start_date: datetime, end_date: datetime, request: Request):
    agenda_service: IAgendaService = inject.instance(IAgendaService)
    current_user = request.state.current_user

    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a la agenda de este usuario.")

    return await agenda_service.get_user_agenda(user_id, start_date, end_date)


@router.get("/agendas/group/{group_id}", response_model=list[UserAgendaResponse])
@require_authentication
async def get_group_agenda(group_id: uuid.UUID, start_date: datetime, end_date: datetime, request: Request):
    agenda_service: IAgendaService = inject.instance(IAgendaService)
    return await agenda_service.get_group_agenda(group_id, start_date, end_date)
