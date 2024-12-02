from typing import List
import uuid
from datetime import datetime

from abc import abstractmethod
from app.application.base_repository import BaseRepository
from app.domain.models.schemma import EventResponse, UserAgendaResponse


class IAgendaRepository(BaseRepository):
    @abstractmethod
    async def get_user_agenda(self, user_id: uuid.UUID, start_date: datetime, end_date: datetime) -> UserAgendaResponse:      
        pass

    @abstractmethod
    async def get_group_agenda(self, group_id: uuid.UUID, start_date: datetime, end_date: datetime) -> List[EventResponse]:
        pass
