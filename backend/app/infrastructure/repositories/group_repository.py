import uuid
from sqlalchemy.future import select

from app.application.repositories.group_repository import IGroupRepository
from app.domain.models.schemma import GroupCreate
from app.domain.models.schemma import GroupResponse
from app.infrastructure.sqlite.tables import Group
from app.infrastructure.repositories.mapper import GroupMapper


class GroupRepository(IGroupRepository):
    mapper = GroupMapper()

    async def create(self, group_create: GroupCreate) -> GroupResponse:
        db = await self.get_db()
        group = self.mapper.to_table(group_create)
        db.add(group)
        await db.commit()
        await db.refresh(group)
        return self.mapper.to_entity(group)

    async def get_by_id(self, group_id: uuid.UUID) -> GroupResponse:
        db = await self.get_db()
        result = await db.execute(select(Group).where(Group.id == group_id))
        group = result.scalars().first()
        return self.mapper.to_entity(group) if group else None

    async def update(self, group_id: uuid.UUID, group_data: GroupCreate) -> GroupResponse:
        db = await self.get_db()
        group = await self.get_by_id(group_id)
        for key, value in group_data.dict().items():
            setattr(group, key, value)
        await db.commit()
        await db.refresh(group)
        return self.mapper.to_entity(group)

    async def delete(self, group_id: uuid.UUID):
        db = await self.get_db()
        group = await self.get_by_id(group_id)
        if group:
            await db.delete(group)
            await db.commit()
        else:
            raise Exception("Group not found")
