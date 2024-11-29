import uuid
from fastapi import HTTPException
from sqlalchemy.future import select

from app.application.repositories.group_repository import IGroupRepository
from app.domain.models.schemma import GroupCreate
from app.domain.models.schemma import GroupResponse
from app.infrastructure.sqlite.tables import Group
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
                return self.mapper.to_entity(group)
            except Exception as e:
                await db.rollback()
                raise e

    async def get_by_id(self, group_id: uuid.UUID) -> GroupResponse:
        async with get_db() as db:
            result = await db.execute(select(Group).where(Group.id == str(group_id)))
            group = result.scalars().first()
            return self.mapper.to_entity(group) if group else None

    async def update(self, group_id: uuid.UUID, group_data: GroupCreate) -> GroupResponse:
        async with get_db() as db:
            group = await self.get_by_id(str(group_id))
            for key, value in group_data.dict().items():
                setattr(group, key, value)
            
            try:
                await self.commit(db)
                await self.refresh(db, group)
                return self.mapper.to_entity(group)
            except Exception as e:
                await db.rollback()
                raise e

    async def delete(self, group_id: uuid.UUID):
        async with get_db() as db:
            group = await self.get_by_id(str(group_id))
            if group:
                try:
                    await db.delete(db, group)
                    await self.commit(db)
                except Exception as e:
                    await db.rollback()
                    raise e
            else:
                raise Exception("Group not found")
    
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
