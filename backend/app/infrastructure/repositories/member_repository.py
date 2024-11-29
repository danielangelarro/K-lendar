import uuid
from sqlalchemy.future import select
from app.application.repositories.member_repository import IMemberRepository
from app.domain.models.schemma import MemberCreate, MemberResponse
from app.infrastructure.sqlite.tables import Member
from app.infrastructure.sqlite.database import get_db
from app.infrastructure.repositories.mapper import MemberMapper


class MemberRepository(IMemberRepository):
    mapper = MemberMapper()

    async def add_member(self, group_id: uuid.UUID, user_id: int) -> MemberResponse:
        async with get_db() as db:
            member = self.mapper.to_table(MemberCreate(user_id=str(user_id), group_id=str(group_id)))
            db.add(member)

            try:
                await self.commit(db)
                await self.refresh(db, member)
                return self.mapper.to_entity(member)
            except Exception as e:
                await db.rollback()
                raise e

    async def remove_member(self, group_id: uuid.UUID, user_id: int) -> bool:
        async with get_db() as db:
            member = await db.execute(select(Member).where(Member.group_id == str(group_id), Member.user_id == str(user_id)))
            member_to_remove = member.scalars().first()
            if member_to_remove:
                try:
                    await db.delete(member_to_remove)
                    await self.commit(db)
                    return True
                except Exception as e:
                    await db.rollback()
                    raise e
            return False
