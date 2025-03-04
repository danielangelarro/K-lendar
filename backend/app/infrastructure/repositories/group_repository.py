import json
from typing import List
import uuid
from fastapi import HTTPException

from app.infrastructure.sqlite.utils import generate_unique_uuid
from app.settings import settings
from app.application.repositories.group_repository import IGroupRepository
from app.domain.models.schemma import GroupCreate, MemberCreate, UserResponse
from app.domain.models.schemma import GroupResponse
from app.infrastructure.repositories.mapper import GroupMapper, MemberMapper


class GroupRepository(IGroupRepository):
    mapper = GroupMapper()
    member_mapper = MemberMapper()

    async def create(self, group_create: GroupCreate) -> GroupResponse:
        group = self.mapper.to_table(group_create)
        await settings.node.store_key(f"groups:{group['id']}", json.dumps(group))

        member = self.member_mapper.to_table(MemberCreate(user_id=group_create.owner.id, group_id=group["id"]))
        await settings.node.store_key(f"member:{member['id']}", json.dumps(member))

        query_payload = json.dumps(
            {"table": "member", "filters": {"group_id": str(group['id'])}}
        )
        members_json = settings.node.ref.get_all_filtered(query_payload)
        members = json.loads(members_json) if members_json else []

        response: GroupResponse = self.mapper.to_entity(group)
        response.cant_members = len(members)
        response.owner_username = group_create.owner.username

        return response

    async def get_by_id(self, group_id: uuid.UUID) -> GroupResponse:
        group_json = await settings.node.retrieve_key(f"groups:{group_id}")
        if not group_json:
            return None
        group = json.loads(group_json)
        return self.mapper.to_entity(group)
    
    async def get_by_user(self, user: UserResponse) -> List[GroupResponse]:        
        response = []

        # Obtener los IDs de los grupos a los que pertenece el usuario desde Chord
        query_payload = json.dumps({"table": "member", "filters": {"user_id": str(user.id)}})
        members_json = settings.node.ref.get_all_filtered(query_payload)
        members = json.loads(members_json) if members_json else []

        group_ids = [member["group_id"] for member in members]

        for group_id in group_ids:
            # Obtener los datos del grupo desde Chord
            group_json = await settings.node.retrieve_key(f"groups:{group_id}")
            if not group_json:
                continue
            group = json.loads(group_json)

            # Contar los miembros del grupo desde Chord
            query_payload = json.dumps({"table": "member", "filters": {"group_id": group_id}})
            members_json = settings.node.ref.get_all_filtered(query_payload)
            members_count = len(json.loads(members_json)) if members_json else 0

            group_entity = self.mapper.to_entity(group)
            group_entity.cant_members = members_count
            group_entity.owner_username = user.username
            group_entity.is_my = group["owner_id"] == str(user.id)

            # Buscar si el grupo tiene un padre en la jerarquía
            query_payload = json.dumps({"table": "group_hierarchy", "filters": {"child_group_id": group_id}})
            hierarchy_json = settings.node.ref.get_all_filtered(query_payload)
            hierarchy = json.loads(hierarchy_json) if hierarchy_json else []

            if hierarchy:
                parent_group_id = hierarchy[0]["parent_group_id"]
                parent_group_json = await settings.node.retrieve_key(f"groups:{parent_group_id}")
                if parent_group_json:
                    parent_group = json.loads(parent_group_json)
                    group_entity.parent = parent_group["group_name"]

            response.append(group_entity)

        return response

    
    async def get_by_name(self, group_name: str) -> GroupResponse:
        query_payload = json.dumps({"table": "groups", "filters": {"group_name": group_name}})
        groups_json = settings.node.ref.get_all_filtered(query_payload)

        group = json.loads(groups_json)[0] if groups_json else None
        
        return self.mapper.to_entity(group) if group else None

    async def update(self, group_id: uuid.UUID, group_data: GroupCreate) -> GroupResponse:
        group_key = f"groups:{group_id}"
        group_json = await settings.node.retrieve_key(group_key)

        if not group_json:
            raise HTTPException(status_code=404, detail="Group not found")
        group = json.loads(group_json)

        if group["owner_id"] != str(group_data.owner.id):
            raise HTTPException(status_code=403, detail="You are not the owner of this group")

        group["group_name"] = group_data.name
        group["description"] = group_data.description

        await settings.node.store_key(group_key, json.dumps(group))
        await settings.node.store_key(f"group_name:{group_data.name}", json.dumps(group))

        return self.mapper.to_entity(group)
    
    async def update_parent(self, group_id: uuid.UUID, parent_group_id: uuid.UUID) -> GroupResponse:
        group_json = await settings.node.retrieve_key(f"groups:{group_id}")
        if not group_json:
            raise HTTPException(status_code=404, detail="Group not found")
        
        group = json.loads(group_json)
        parent_json = await settings.node.retrieve_key(f"groups:{parent_group_id}")
        
        if not parent_json:
            raise HTTPException(status_code=404, detail="Parent group not found")
        
        hierarchy = {
            "id": generate_unique_uuid(parent_group_id, group_id),
            "parent_group_id": str(parent_group_id),
            "child_group_id": str(group_id)
        }
        await settings.node.store_key(f"group_hierarchy:{hierarchy['id']}", json.dumps(hierarchy))
        
        return self.mapper.to_entity(group)

    async def delete(self, group_id: uuid.UUID, user_id: uuid.UUID):
        group_json = await settings.node.retrieve_key(f"groups:{group_id}")
        if not group_json:
            raise HTTPException(status_code=404, detail="Group not found")
        group = json.loads(group_json)
        
        if group["owner_id"] != str(user_id):
            raise HTTPException(status_code=403, detail="You are not the owner of this group")
        
        await settings.node.delete_key(f"groups:{group_id}")

        # Remove members
        payload = {
            "table": "member",
            "filters": {"group_id": str(group_id)},
        }
        members_json = settings.node.ref.get_all_filtered(json.dumps(payload))

        if members_json:
            members = json.loads(members_json)
            for member in members:
                await settings.node.delete_key(f"member:{member['id']}")
        
        # Remove hierachy
        payload = {
            "table": "group_hierarchy",
            "filters": {"parent_group_id": str(group_id)},
        }
        gh_json = settings.node.ref.get_all_filtered(json.dumps(payload))
        
        if gh_json:
            ghs = json.loads(members_json)
            
            for gh in ghs:
                await settings.node.delete_key(f"group_hierarchy:{gh['id']}")
        
        return {"message": "Group deleted successfully"}
        
    async def set_parent_group(self, group_id: uuid.UUID, parent_group_id: uuid.UUID):
        return await self.update_parent(group_id, parent_group_id)
