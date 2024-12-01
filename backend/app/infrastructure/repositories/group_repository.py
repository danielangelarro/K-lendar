from typing import List
import uuid
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.future import select

from app.application.repositories.group_repository import IGroupRepository
from app.domain.models.schemma import GroupCreate, UserResponse
from app.domain.models.schemma import GroupResponse
from app.infrastructure.sqlite.tables import Group, Member
from app.infrastructure.sqlite.database import get_db
from app.infrastructure.sqlite.database import get_db
from app.infrastructure.repositories.mapper import GroupMapper


class GroupRepository(IGroupRepository):
    mapper = GroupMapper()

    async def create(self, group_create: GroupCreate) -> GroupResponse:
        async with get_db() as db:
            group = self.mapper.to_table(group_create)
            db.add(group)

            try:
                await self.commit(db)
                await self.refresh(db, group)

                member = Member(user_id=str(group_create.owner.id), group_id=str(group.id))
                db.add(member)
                await self.commit(db)

                members_query = await db.execute(select(Member).where(Member.group_id == str(group.id)))
                members = [member.user_id for member in members_query.scalars().all()]
                
                response: GroupResponse = self.mapper.to_entity(group)
                response.cant_members = len(members)
                response.owner_username = group_create.owner.username

                return response
            except Exception as e:
                await db.rollback()
                raise e

    async def get_by_id(self, group_id: uuid.UUID) -> GroupResponse:
        async with get_db() as db:
            result = await db.execute(select(Group).where(Group.id == str(group_id)))
            group = result.scalars().first()
            return self.mapper.to_entity(group) if group else None
    
    async def get_by_user(self, user: UserResponse) -> List[GroupResponse]:
        async with get_db() as db:
            result = await db.execute(
                select(
                    Group,
                    func.count(Member.user_id).label('member_count')
                )
                .outerjoin(Member, Member.group_id == Group.id)
                .where(Group.id.in_(
                    select(Member.group_id)
                    .where(Member.user_id == str(user.id))
                ))
                .group_by(Group.id)
            )
            
            groups = result.all()
            response = []

            for group, member_count in groups:
                response.append(self.mapper.to_entity(group))
                response[-1].cant_members = member_count
                response[-1].owner_username = user.username
                response[-1].is_my = group.owner_id == str(user.id)
            
            return response

    async def get_by_name(self, group_name: str) -> GroupResponse:
        async with get_db() as db:
            result = await db.execute(select(Group).where(Group.group_name == group_name))
            group = result.scalars().first()
            return self.mapper.to_entity(group) if group else None

    async def update(self, group_id: uuid.UUID, group_data: GroupCreate) -> GroupResponse:
        async with get_db() as db:
            try:
                await db.begin()

                result = await db.execute(select(Group).where(Group.id == str(group_id)))
                group = result.scalars().first()

                if not group:
                    raise HTTPException(status_code=404, detail="Group not found")
                
                if group.owner_id != str(group_data.owner.id):
                    raise HTTPException(status_code=403, detail="You are not the owner of this group")
                
                group.group_name = group_data.name
                group.description = group_data.description

                await db.flush()
                await self.commit(db)
                await self.refresh(db, group)
                return self.mapper.to_entity(group)
            except Exception as e:
                await db.rollback()
                raise e
            finally:
                await db.close()
    
    async def delete(self, group_id: uuid.UUID, user_id: uuid.UUID):
        async with get_db() as db:
            try:
                await db.begin()
                result = await db.execute(select(Group).where(Group.id == str(group_id)))
                group = result.scalars().first()
                
                if not group:
                    raise HTTPException(status_code=404, detail="Group not found")
                
                if group.owner_id != str(user_id):
                    raise HTTPException(status_code=403, detail="You are not the owner of this group")

                result_members = await db.execute(select(Member).where(Member.group_id == str(group_id)))
                members = result_members.scalars().all()
                
                for member in members:
                    await db.delete(member)
                
                await db.delete(group)                
                await db.commit()
                
                return {"message": "Group deleted successfully"}
            
            except Exception as e:
                await db.rollback()
                
                if isinstance(e, HTTPException):
                    raise
                else:
                    raise HTTPException(status_code=500, detail="Internal server error deleting group")
            finally:
                await db.close()
        
    async def set_parent_group(self, group_id: uuid.UUID, parent_group_id: uuid.UUID):
        async with get_db() as db:
            group = await self.get_by_id(str(group_id))
            parent_group = await self.get_by_id(str(parent_group_id))

            if not group or not parent_group:
                raise HTTPException(status_code=404, detail="Grupo o grupo padre no encontrado.")

            group.parent_group_id = parent_group_id
            
            try:
                await db.commit()
                await db.refresh(group)
                return group
            except Exception as e:
                await db.rollback()
                raise e
