import json
import logging

from fastapi import APIRouter
from sqlalchemy import select
from app.settings import settings
from app.domain.models.schemma import KeysPayload
from backend.app.domain.distribute.chord import TABLE_MAP
from backend.app.infrastructure.sqlite.database import get_db

router = APIRouter()


@router.get("/successor")
async def get_successor():
    successor = settings.node.succ
    logging.info(f"Endpoint /successor llamado: {successor}")
    return {"successor": str(successor)}


@router.get("/predecessor")
async def get_predecessor():
    predecessor = settings.node.pred
    logging.info(f"Endpoint /predecessor llamado: {predecessor}")
    return {"predecessor": str(predecessor) if predecessor else None}


@router.post("/receive_keys")
async def receive_keys(payload: KeysPayload):
    if not payload.keys:
        return {"status": "success", "message": "No keys to transfer"}
    
    received = {item.key: item.value for item in payload.keys}
    tables = ['users', 'events', 'group_hierarchy', 'groups', 'user_event', 'member', 'notification']
    current = {}
    
    async with get_db() as session:
        # Obtener las llaves actuales de cada tabla
        for table in tables:
            model = TABLE_MAP.get(table)
            if not model:
                continue
            result = await session.execute(select(model.id))
            for id in result.scalars().all():
                current[f"{table}:{id}"] = True
        
        # Insertar/Actualizar las llaves recibidas
        for key, value in received.items():
            table, entity_id = key.split(':', 1)
            model = TABLE_MAP.get(table)
            if not model:
                continue
            data = json.loads(value)
            data['id'] = entity_id
            instance = model(**data)
            session.merge(instance)
        
        # Eliminar las llaves que ya no están presentes
        keys_to_delete = set(current.keys()) - set(received.keys())
        
        for key in keys_to_delete:
            table, entity_id = key.split(':', 1)
            model = TABLE_MAP.get(table)
            if not model:
                continue
            obj = await session.get(model, entity_id)
            if obj:
                await session.delete(obj)
        
        await session.commit()
    
    logging.info("Llaves recibidas y almacenadas")
    return {"status": "success", "message": "Keys received"}
