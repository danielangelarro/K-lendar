import uuid
from sqlalchemy.future import select
from app.application.repositories.member_repository import IMemberRepository
from app.domain.models.schemma import MemberCreate, MemberResponse
from app.infrastructure.sqlite.tables import Member
from app.infrastructure.repositories.mapper import MemberMapper


class MemberRepository(IMemberRepository):
    mapper = MemberMapper()

    async def add_member(self, group_id: uuid.UUID, user_id: int) -> MemberResponse:
        db = await self.get_db()
        member = self.mapper.to_table(MemberCreate(user_id=str(user_id), group_id=str(group_id)))
        db.add(member)
        await db.commit()
        await db.refresh(member)
        return self.mapper.to_entity(member)

    async def remove_member(self, group_id: uuid.UUID, user_id: int) -> bool:
        db = await self.get_db()
        member = await db.execute(select(Member).where(Member.group_id == str(group_id), Member.user_id == str(user_id)))
        member_to_remove = member.scalars().first()
        if member_to_remove:
            await db.delete(member_to_remove)
            await db.commit()
            return True
        return False
