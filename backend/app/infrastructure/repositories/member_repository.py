from collections import deque
from fastapi import HTTPException
import json
from typing import List
import uuid

from app.infrastructure.sqlite.utils import generate_uuid
from app.settings import settings
from app.application.repositories.member_repository import IMemberRepository
from app.domain.models.schemma import MemberCreate, MemberResponse, UserResponse

from app.infrastructure.repositories.mapper import MemberMapper, UserMapper


class MemberRepository(IMemberRepository):
    mapper = MemberMapper()
    user_mapper = UserMapper()

    async def add_member(self, group_id: uuid.UUID, email: str) -> MemberResponse:
        query_payload = json.dumps(
            {
                "table": "users",
                "filters": {"email": email},
            }
        )
        users_json = settings.node.ref.get_all_filtered(query_payload)
        users_list = json.loads(users_json) if users_json else []
        user = users_list[0] if users_list else None

        if not user:
            raise Exception("User not found")

        group_json = await settings.node.retrieve_key(f"groups:{group_id}")
        if not group_json:
            raise Exception("Group not found")
        group = json.loads(group_json)

        member = self.mapper.to_table(
            MemberCreate(user_id=user["id"], group_id=group_id)
        )
        await settings.node.store_key(f"member:{member['id']}", json.dumps(member))

        notification = {
            "id": str(generate_uuid()),
            "recipient": str(user["id"]),
            "sender": group["owner_id"],
            "title": "Group Notifications",
            "message": f"You have been added to {group['group_name']} group. Do you want to stay or leave?",
            "is_read": False
        }
        await settings.node.store_key(
            f"notification:{notification['id']}", json.dumps(notification)
        )

        return self.mapper.to_entity(member)

    async def get_members(self, group_id: uuid.UUID) -> List[UserResponse]:
        query_payload = json.dumps(
            {"table": "member", "filters": {"group_id": str(group_id)}}
        )
        members_json = settings.node.ref.get_all_filtered(query_payload)
        members_list = json.loads(members_json) if members_json else []
        result = []

        for member in members_list:
            user_json = await settings.node.retrieve_key(f"users:{member['user_id']}")
            if user_json:
                user = json.loads(user_json)
                result.append(self.user_mapper.to_entity(user))
        return result

    async def get_child_groups(self, group_id: uuid.UUID) -> List[UserResponse]:
        queue = deque([str(group_id)])
        visited_groups = set()
        all_group_ids = set()

        while queue:
            current_group_id = queue.popleft()

            query_payload = json.dumps(
                {
                    "table": "group_hierarchy",
                    "filters": {"parent_group_id": current_group_id},
                }
            )
            gh_json = settings.node.ref.get_all_filtered(query_payload)
            child_groups = json.loads(gh_json) if gh_json else []

            for child in child_groups:
                child_id = child["child_group_id"]
                if child_id not in visited_groups:
                    visited_groups.add(child_id)
                    queue.append(child_id)
            all_group_ids.add(current_group_id)

        unique_users = {}
        for gid in all_group_ids:
            query_payload = json.dumps(
                {"table": "member", "filters": {"group_id": gid}}
            )
            mem_json = settings.node.ref.get_all_filtered(query_payload)
            mems = json.loads(mem_json) if mem_json else []

            for m in mems:
                user_json = await settings.node.retrieve_key(f"users:{m['user_id']}")
                if user_json:
                    user = json.loads(user_json)
                    unique_users[user["id"]] = user
        return [self.user_mapper.to_entity(user) for user in unique_users.values()]

    async def remove_member(self, group_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        
        query_payload = json.dumps(
            {
                "table": "member",
                "filters": {"group_id": str(group_id), "user_id": str(user_id)},
            }
        )
        member_json = settings.node.ref.get_all_filtered(query_payload)
        member_list = json.loads(member_json) if member_json else []
        
        if not member_list:
            return False
        
        member_to_remove = member_list[0]
        group_json = await settings.node.retrieve_key(f"groups:{group_id}")
        
        if not group_json:
            raise HTTPException(status_code=404, detail="Group not found")
        
        group = json.loads(group_json)
        await settings.node.delete_key(f"member:{member_to_remove['id']}")
        
        notification = {
            "id": str(generate_uuid()),
            "recipient": str(user_id),
            "sender": group["owner_id"],
            "message": f"You have been removed from {group['group_name']} group.",
            "title": "Group Notifications",
            "is_read": False,
        }
        await settings.node.store_key(
            f"notification:{notification['id']}", json.dumps(notification)
        )
        
        return True
