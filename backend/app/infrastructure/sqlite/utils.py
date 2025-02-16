import uuid
import hashlib

def generate_unique_uuid(uuid1: uuid.UUID, uuid2: uuid.UUID) -> uuid.UUID:
    uuid1_str = str(uuid1)
    uuid2_str = str(uuid2)
    
    combined_str = uuid1_str + uuid2_str
    
    hash_object = hashlib.sha256(combined_str.encode('utf-8'))    
    hash_bytes = hash_object.digest()[:16]
    
    new_uuid = uuid.UUID(bytes=hash_bytes)
    
    return new_uuid

def generate_uuid() -> uuid.UUID:
    return str(uuid.uuid4())
