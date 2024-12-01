from typing import List
import uuid
from sqlalchemy.future import select
from app.application.repositories.member_repository import IMemberRepository
from app.domain.models.schemma import MemberCreate, MemberResponse, UserResponse
from app.infrastructure.sqlite.tables import Group, Member, Notification, User
from app.infrastructure.sqlite.database import get_db
from app.infrastructure.repositories.mapper import MemberMapper, UserMapper


class MemberRepository(IMemberRepository):
    mapper = MemberMapper()
    user_mapper = UserMapper()

    async def add_member(self, group_id: uuid.UUID, email: str) -> MemberResponse:
        async with get_db() as db:
            await db.begin()

            result = await db.execute(select(User).where(User.email == email))
            user = result.scalars().first()

            result = await db.execute(select(Group).where(Group.id == str(group_id)))
            group = result.scalars().first()

            member = self.mapper.to_table(MemberCreate(user_id=str(user.id), group_id=str(group_id)))
            notification = Notification(
                recipient=user.id,
                sender=group.owner_id,
                message=f"You have been added to {group.group_name} group.",
            )
            
            db.add(member)
            db.add(notification)

            try:
                await self.commit(db)
                await self.refresh(db, member)
                return self.mapper.to_entity(member)
            except Exception as e:
                await db.rollback()
                raise e
    
    async def get_members(self, group_id: uuid.UUID) -> List[UserResponse]:
         async with get_db() as db:
            results = await db.execute(
                select(User)
                .join(Member, User.id == Member.user_id)
                .where(Member.group_id == str(group_id))
            )
            members = results.scalars().all()

            try:
                return [self.user_mapper.to_entity(member) for member in members]
            except Exception as e:
                await db.rollback()
                raise e
        

    async def remove_member(self, group_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        async with get_db() as db:
            await db.begin()

            member = await db.execute(select(Member).where(Member.group_id == str(group_id), Member.user_id == str(user_id)))
            member_to_remove = member.scalars().first()

            result = await db.execute(select(Group).where(Group.id == str(group_id)))
            group = result.scalars().first()

            if member_to_remove:
                try:
                    await db.delete(member_to_remove)

                    notification = Notification(
                        recipient=str(user_id),
                        sender=group.owner_id,
                        message=f"You have been removed from {group.group_name} group.",
                    )

                    db.add(notification)

                    await self.commit(db)
                    return True
                except Exception as e:
                    await db.rollback()
                    raise e
            return False
