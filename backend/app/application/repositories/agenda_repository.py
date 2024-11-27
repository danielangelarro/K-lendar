from typing import List
import uuid
from datetime import datetime

from abc import abstractmethod
from app.application.base_repository import BaseRepository
from app.domain.models.schemma import AgendaEventResponse, UserAgendaResponse


class IAgendaRepository(BaseRepository):
    @abstractmethod
    async def get_user_agenda(self, user_id: uuid.UUID, start_date: datetime, end_date: datetime) -> UserAgendaResponse:      
        pass

    @abstractmethod
    async def get_group_agenda(self, group_id: uuid.UUID, start_date: datetime, end_date: datetime) -> List[UserAgendaResponse]:
        pass

    @abstractmethod
    def map_event_to_response(self, event) -> AgendaEventResponse:
        pass