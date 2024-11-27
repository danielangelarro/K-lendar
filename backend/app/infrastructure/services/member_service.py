import uuid
import inject
from app.application.repositories.member_repository import IMemberRepository


class MemberService:
    repo_instance: IMemberRepository = inject.attr(IMemberRepository)

    async def add_member(self, group_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        await self.repo_instance.add_member(group_id, user_id)
        return True

    async def remove_member(self, group_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        return await self.repo_instance.remove_member(group_id, user_id)
