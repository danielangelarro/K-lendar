import uuid
import inject

from app.application.services.group_service import IGroupService
from app.application.repositories.group_repository import IGroupRepository
from app.domain.models.schemma import GroupCreate
from app.domain.models.schemma import GroupResponse


class GroupService(IGroupService):
    repo_instance: IGroupRepository = inject.attr(IGroupRepository)

    async def create_group(self, group: GroupCreate) -> GroupResponse:
        return await self.repo_instance.create(group)

    async def get_group(self, group_id: uuid.UUID) -> GroupResponse:
        return await self.repo_instance.get_by_id(group_id)

    async def update_group(self, group_id: uuid.UUID, group_data: GroupCreate) -> GroupResponse:
        return await self.repo_instance.update(group_id, group_data)

    async def delete_group(self, group_id: uuid.UUID):
        await self.repo_instance.delete(group_id)
