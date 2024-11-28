import uuid
from typing import List
from datetime import datetime
from abc import ABC, abstractmethod

from app.domain.models.schemma import UserAgendaResponse


class IAgendaService(ABC):
    @abstractmethod
    async def get_user_agenda(self, user_id: uuid.UUID, start_date: datetime, end_date: datetime) -> UserAgendaResponse:
        pass

    @abstractmethod
    async def get_group_agenda(self, group_id: uuid.UUID, start_date: datetime, end_date: datetime) -> List[UserAgendaResponse]:
        pass
