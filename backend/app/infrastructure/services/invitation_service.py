import uuid
import inject
from typing import List

from app.application.services.invitation_service import IInvitationService
from app.application.repositories.invitation_repository import IInvitationRepository


class InvitationService(IInvitationService):
    repo_instance: IInvitationRepository = inject.attr(IInvitationRepository)

    async def invite_users(self, event_id: uuid.UUID, user_ids: List[uuid.UUID], group_id: uuid.UUID) -> None:
        await self.repo_instance.invite_users(event_id, user_ids, group_id)

    async def accept_invitation(self, event_id: uuid.UUID, user_id: uuid.UUID) -> None:
        await self.repo_instance.accept_invitation(event_id, user_id)

    async def decline_invitation(self, event_id: uuid.UUID, user_id: uuid.UUID) -> None:
        await self.repo_instance.decline_invitation(event_id, user_id)
