from datetime import datetime
import json
import logging

from fastapi import APIRouter
from sqlalchemy import select
from app.settings import settings
from app.domain.models.schemma import KeysPayload
from app.domain.distribute.chord import TABLE_MAP
from app.infrastructure.sqlite.database import get_db

router = APIRouter()


@router.get("/successor")
async def get_successor():
    successor = settings.node.ref.succ
    return {"successor": str(successor)}


@router.get("/predecessor")
async def get_predecessor():
    predecessor = settings.node.ref.pred
    return {"predecessor": str(predecessor) if predecessor else None}


@router.post("/receive_keys")
async def receive_keys(payload: KeysPayload):
    if not payload.keys:
        return {"status": "success", "message": "No keys to transfer"}
    
    received = {item.key: item.value for item in payload.keys}
    tables = ['users', 'events', 'group_hierarchy', 'groups', 'user_event', 'member', 'notification']
    current = {}
    updated_at = datetime.min
    
    async with get_db() as session:
        try:
            # Obtener las llaves actuales de cada tabla
            for table in tables:
                model = TABLE_MAP.get(table)
                if not model:
                    continue
                result = await session.execute(select(model.id, model.created_at, model.updated_at))
                for id, c_at, u_at in result.scalars().all():
                    current[f"{table}:{id}"] = True
                    
                    if u_at and u_at > updated_at:
                        updated_at = u_at
                    else:
                        updated_at = c_at
        
            if updated_at > payload.updated_at:
                return {"status": "success", "message": "Keys not updated, before my keys"}
            
            for key, value in received.items():
                table, entity_id = key.split(':', 1)
                model = TABLE_MAP.get(table)
                if not model:
                    continue
                
                try:
                    data = json.loads(value)
                    for k, v in data.items():
                        if isinstance(v, str):
                            try:
                                # Intentar convertir a datetime si parece ser una fecha ISO
                                data[k] = datetime.fromisoformat(v)
                            except ValueError:
                                # Si no es un formato de fecha válido, dejarlo como está
                                pass
                except json.JSONDecodeError as e:
                    return

                data['id'] = entity_id
                instance = model(**data)
                await session.merge(instance)
        
            # print("Eliminar las llaves que ya no están presentes")
            # keys_to_delete = set(current.keys()) - set(received.keys())
            
            # for key in keys_to_delete:
            #     table, entity_id = key.split(':', 1)
            #     model = TABLE_MAP.get(table)
            #     if not model:
            #         continue
            #     obj = await session.get(model, entity_id)
            #     if obj:
            #         await session.delete(obj)
            
            await session.commit()
        except Exception as e:
            print("Error en receive_keys", e)
    
    return {"status": "success", "message": "Keys received"}
