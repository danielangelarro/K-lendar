import asyncio
from datetime import datetime
import socket
import threading
import time
import hashlib
import json
import logging
from typing import List, Optional

import requests

from app.infrastructure.sqlite.database import get_db
from sqlalchemy import select, and_
from app.infrastructure.sqlite.tables import (
    User,
    Event,
    GroupHierarchy,
    Group,
    UserEvent,
    Member,
    Notification,
)

# Diccionario de mapeo: nombre de tabla (string) → clase del modelo
TABLE_MAP = {
    "users": User,
    "events": Event,
    "group_hierarchy": GroupHierarchy,
    "groups": Group,
    "user_event": UserEvent,
    "member": Member,
    "notification": Notification,
}

MULTICAST_GROUP = "224.0.0.1"
PROXY_MULTICAST_PORT = 10000

DELIMITER = '<<DELIM>>'

# Códigos de operación (para comunicación entre nodos Chord)
FIND_SUCCESSOR = 1
FIND_PREDECESSOR = 2
GET_SUCCESSOR = 3
GET_PREDECESSOR = 4
NOTIFY = 5
CHECK_PREDECESSOR = 6
CLOSEST_PRECEDING_FINGER = 7
STORE_KEY = 8
RETRIEVE_KEY = 9
REPLICATE_KEY = 10
TRANSFER_KEYS = 11
GET_ALL_KEYS = 12
DELETE_KEY = 13
GET_ALL_FILTERED = 14


def getShaRepr(data: str) -> int:
    return int(hashlib.sha1(data.encode()).hexdigest(), 16)


class ChordNodeReference:
    def __init__(self, ip: str, port: int = 8001):
        self.id = getShaRepr(ip)
        self.ip = ip
        self.port = port

    def _send_data(self, op: int, data: Optional[str] = None) -> bytes:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.ip, self.port))
                message = f"{op}{DELIMITER}{data if data is not None else ''}"
                s.sendall(message.encode("utf-8"))
                logging.info(f"Enviado: {message} a {self.ip}:{self.port}")
                return s.recv(4096)
        except Exception as e:
            logging.error(
                f"Error enviando datos (op {op}) a {self.ip}:{self.port} - {e}"
            )
            return b""

    def find_successor(self, id_val: int) -> "ChordNodeReference":
        response = self._send_data(FIND_SUCCESSOR, str(id_val)).decode().split(",")
        logging.info(f"find_successor({id_val}) -> {response}")
        return ChordNodeReference(response[1], self.port)

    def find_predecessor(self, id_val: int) -> "ChordNodeReference":
        response = self._send_data(FIND_PREDECESSOR, str(id_val)).decode().split(",")
        logging.info(f"find_predecessor({id_val}) -> {response}")
        return ChordNodeReference(response[1], self.port)

    @property
    def succ(self) -> "ChordNodeReference":
        response = self._send_data(GET_SUCCESSOR).decode().split(",")
        logging.info(f"GET_SUCCESSOR -> {response}")
        return ChordNodeReference(response[1], self.port)

    @property
    def pred(self) -> "ChordNodeReference":
        response = self._send_data(GET_PREDECESSOR).decode().split(",")
        logging.info(f"GET_PREDECESSOR -> {response}")
        return ChordNodeReference(response[1], self.port)

    def notify(self, node: "ChordNodeReference"):
        logging.info(f"Notificando a {self.ip}:{self.port} con nodo {node.ip}")
        self._send_data(NOTIFY, f"{node.id},{node.ip}")

    def check_predecessor(self):
        self._send_data(CHECK_PREDECESSOR)

    def closest_preceding_finger(self, id_val: int) -> "ChordNodeReference":
        response = (
            self._send_data(CLOSEST_PRECEDING_FINGER, str(id_val)).decode().split(",")
        )
        logging.info(f"closest_preceding_finger({id_val}) -> {response}")
        return ChordNodeReference(response[1], self.port)

    def store_key(self, key: str, value: str):
        self._send_data(STORE_KEY, f"{key},{value}")

    def retrieve_key(self, key: str) -> str:
        return self._send_data(RETRIEVE_KEY, key).decode()

    def delete_key(self, key: str) -> str:
        return self._send_data(DELETE_KEY, key).decode()

    def get_all_filtered(self, query_payload: str) -> str:
        response = self._send_data(GET_ALL_FILTERED, query_payload)
        return response.decode()

    def __str__(self) -> str:
        return f"{self.id},{self.ip},{self.port}"

    def __repr__(self) -> str:
        return str(self)


class ChordNode:
    def __init__(self, ip: str, port: int = 8001, m: int = 160):
        self.id = getShaRepr(ip)
        self.ip = ip
        self.port = port
        self.ref = ChordNodeReference(self.ip, self.port)
        self.succ = self.ref
        self.pred = None
        self.m = m
        self.finger = [self.ref] * self.m
        self.next = 0
        self.db_lock = threading.Lock()
        logging.info(f"Inicializado ChordNode en {self.ip}:{self.port}")

    def start_services(self):
        """Inicia los hilos del protocolo Chord."""
        logging.info("Iniciando servicios de Chord...")
        threading.Thread(target=self.stabilize, daemon=True).start()
        threading.Thread(target=self.fix_fingers, daemon=True).start()
        threading.Thread(target=self.check_predecessor, daemon=True).start()
        threading.Thread(target=self.start_server, daemon=True).start()
        threading.Thread(target=self.multicast_listener, daemon=True).start()
        threading.Thread(target=self.announce_self, daemon=True).start()
    
    def announce_self(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        message = f'{self.ip},{self.port}'.encode()
        while True:
            try:
                sock.sendto(message, (MULTICAST_GROUP, PROXY_MULTICAST_PORT))
                logging.info(f"Anunciando presencia: {self.ip}:{self.port}")
            except Exception as e:
                logging.error(f"Error en announce_self: {e}")
            time.sleep(5)

    def multicast_listener(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', PROXY_MULTICAST_PORT))
        mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton("0.0.0.0")
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                node_ip, node_port = data.decode().split(',')
                logging.info(f"Descubierto nodo: {node_ip}:{node_port}")
                if node_ip != self.ip and (self.succ.id == self.id or self.succ.pred != self.id):
                    self.join(ChordNodeReference(node_ip, int(node_port)))
            except Exception as e:
                logging.error(f"Error en multicast_listener: {e}")

    def _inbetween(self, k: int, start: int, end: int) -> bool:
        if start < end:
            return start < k <= end
        else:
            return start < k or k <= end

    def find_succ(self, id: int) -> "ChordNodeReference":
        node = self.find_pred(id)
        return node.succ

    def find_pred(self, id: int) -> "ChordNodeReference":
        node = self
        while not self._inbetween(id, node.id, node.succ.id):
            node = node.closest_preceding_finger(id)
        return node

    def closest_preceding_finger(self, id: int) -> "ChordNodeReference":
        for i in range(self.m - 1, -1, -1):
            if self.finger[i] and self._inbetween(self.finger[i].id, self.id, id):
                return self.finger[i]
        return self.ref

    async def join(self, node: "ChordNodeReference"):
        logging.info(f"Uniéndose al nodo: {node.ip}:{node.port}")
        if node:
            self.pred = None
            self.succ = node.find_successor(self.id)
            logging.info(f"Nuevo sucesor determinado: {self.succ.ip}:{self.succ.port}")
            self.succ.notify(self.ref)
            # Transferir llaves al nuevo nodo
            await self.transfer_keys_to(self.succ)
        else:
            self.succ = self.ref
            self.pred = None

    def stabilize(self):
        while True:
            try:
                if self.succ.id != self.id:
                    x = self.succ.pred
                    if (
                        x
                        and x.id != self.id
                        and self._inbetween(x.id, self.id, self.succ.id)
                    ):
                        logging.info(
                            f"Stabilize: actualizando sucesor de {self.ip} a {x.ip}"
                        )
                        self.succ = x
                    self.succ.notify(self.ref)
                else:
                    logging.info("Stabilize: sucesor es el mismo nodo.")
            except Exception as e:
                logging.error(f"Error en stabilize: {e}")
            time.sleep(10)

    async def notify(self, node: "ChordNodeReference"):
        logging.info(f"Recibiendo notify de {node.ip}:{node.port}")
        if node.id == self.id:
            return
        if not self.pred or self._inbetween(node.id, self.pred.id, self.id):
            old_pred = self.pred
            self.pred = node
            logging.info(f"Actualizado predecesor a {node.ip}:{node.port}")
            if old_pred is None or old_pred.id != node.id:
                await self.transfer_keys_to(node)

    def fix_fingers(self):
        while True:
            try:
                self.next = (self.next + 1) % self.m
                self.finger[self.next] = self.find_succ(
                    (self.id + 2**self.next) % (2**self.m)
                )
                logging.info(
                    f"finger[{self.next}] actualizado a {self.finger[self.next].ip}"
                )
            except Exception as e:
                logging.error(f"Error en fix_fingers: {e}")
            time.sleep(10)

    def check_predecessor(self):
        while True:
            try:
                if self.pred:
                    self.pred.check_predecessor()
                    logging.info("check_predecessor ejecutado")
            except Exception as e:
                logging.error(f"Error en check_predecessor: {e}")
                self.pred = None
            time.sleep(10)

    # ------------------ Métodos de acceso a datos usando SQLAlchemy ------------------

    async def _handle_get_all_filtered(self, query_payload: str) -> str:
        """
        Recibe un payload JSON con la estructura:
         { "table": "events", "filters": { "start_datetime": {"gte": "..."},
                                             "end_datetime": {"lte": "..."},
                                             "creator": "..." } }
        Construye la consulta usando SQLAlchemy y devuelve los resultados en JSON.
        """
        try:
            query_data = json.loads(query_payload)
            table = query_data.get("table")
            filters = query_data.get("filters", {})
            Model = TABLE_MAP.get(table)
            if not Model:
                return json.dumps([])

            query = select(Model)
            conditions = []
            # Construir condiciones: se soporta operadores "gte", "lte", "gt", "lt" y "eq"
            for field, condition in filters.items():
                column = getattr(Model, field, None)
                if not column:
                    continue
                if isinstance(condition, dict):
                    if "gte" in condition:
                        conditions.append(column >= condition["gte"])
                    if "lte" in condition:
                        conditions.append(column <= condition["lte"])
                    if "gt" in condition:
                        conditions.append(column > condition["gt"])
                    if "lt" in condition:
                        conditions.append(column < condition["lt"])
                    if "eq" in condition:
                        conditions.append(column == condition["eq"])
                else:
                    conditions.append(column == condition)
            if conditions:
                query = query.where(and_(*conditions))

            async with get_db() as session:
                result = await session.execute(query)
                rows = result.scalars().all()
                items = []
                for row in rows:
                    row_dict = {}
                    for k, v in row.__dict__.items():
                        if not k.startswith("_"):
                            if isinstance(v, datetime):
                                row_dict[k] = v.isoformat()
                            else:
                                row_dict[k] = v
                    items.append(row_dict)

            return json.dumps(items)
        except Exception as e:
            logging.error(f"Error en _handle_get_all_filtered: {e}")
            return json.dumps([])

    async def store_key(self, key: str, value: str, replica: bool = False):
        """
        Si el nodo actual es el primario para la llave (según Chord),
        se realiza un "upsert" (merge) sobre la tabla correspondiente.
        Si no, se redirige la operación al nodo primario.
        """
        key_hash = getShaRepr(key)
        primary_node = self.find_succ(key_hash)
        if primary_node.id == self.id:
            if ":" not in key:
                logging.error(f"Clave inválida: {key}")
                return
            table, id = key.split(":", 1)
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
                logging.error(f"Error parseando valor para {key}: {e}")
                return
            Model = TABLE_MAP.get(table)
            if not Model:
                logging.error(f"Modelo para tabla '{table}' no encontrado.")
                return
            data["id"] = id

            async def _store():
                async with get_db() as session:
                    await session.merge(Model(**data))
                    await session.commit()

            await _store()
            
            logging.info(f"Clave '{key}' almacenada en nodo primario {self.ip}")
            if not replica:
                try:
                    succ1 = self.succ
                    succ2 = succ1.succ
                    succ1._send_data(REPLICATE_KEY, f"{key},{value}")
                    succ2._send_data(REPLICATE_KEY, f"{key},{value}")
                    logging.info(f"Clave '{key}' replicada a {succ1.ip} y {succ2.ip}")
                except Exception as e:
                    logging.error(f"Error replicando la clave '{key}': {e}")
        else:
            logging.info(
                f"Redirigiendo clave '{key}' al nodo primario {primary_node.ip}"
            )
            primary_node.store_key(key, value)

    async def direct_store_key(self, key: str, value: str):
        """Almacena la llave directamente (por ejemplo, en transferencia recibida)."""
        if ":" not in key:
            logging.error(f"Clave inválida: {key}")
            return
        table, id = key.split(":", 1)
        try:
            data = json.loads(value)
        except json.JSONDecodeError as e:
            logging.error(f"Error parseando valor para {key}: {e}")
            return
        Model = TABLE_MAP.get(table)
        if not Model:
            logging.error(f"Modelo para tabla '{table}' no encontrado.")
            return
        data["id"] = id

        async def _store():
            async with get_db() as session:
                await session.merge(Model(**data))
                await session.commit()

        await _store()
        logging.info(f"Clave '{key}' almacenada directamente (transferencia recibida)")

    async def retrieve_key(self, key: str) -> str:
        key_hash = getShaRepr(key)
        primary_node = self.find_succ(key_hash)
        if primary_node.id == self.id:
            if ":" not in key:
                return None
            table, id = key.split(":", 1)
            Model = TABLE_MAP.get(table)
            if not Model:
                logging.error(f"Modelo para tabla '{table}' no encontrado.")
                return None

            async def _retrieve():
                async with get_db() as session:
                    result = await session.get(Model, id)
                    if result:
                        # Filtramos atributos internos y devolvemos un JSON
                        data = {}
                        for k, v in result.__dict__.items():
                            if not k.startswith("_"):
                                if isinstance(v, datetime):
                                    data[k] = v.isoformat()
                                else:
                                    data[k] = v
                        return json.dumps(data)
                    return None

            return await _retrieve() or ""
        else:
            logging.info(
                f"Redirigiendo recuperación de clave '{key}' al nodo {primary_node.ip}"
            )
            return primary_node.retrieve_key(key)

    async def delete_key(self, key: str, replicate: bool = False):
        key_hash = getShaRepr(key)
        primary_node = self.find_succ(key_hash)
        if primary_node.id == self.id:
            if ":" not in key:
                logging.error(f"Clave inválida: {key}")
                return
            table, id = key.split(":", 1)
            Model = TABLE_MAP.get(table)
            if not Model:
                logging.error(f"Modelo para tabla '{table}' no encontrado.")
                return

            async def _delete():
                async with get_db() as session:
                    obj = await session.get(Model, id)
                    if obj:
                        await session.delete(obj)
                        await session.commit()

            await _delete()
            logging.info(f"Clave '{key}' borrada en nodo primario {self.ip}")
            if not replicate:
                try:
                    succ1 = self.succ
                    succ2 = succ1.succ
                    succ1._send_data(DELETE_KEY, key)
                    succ2._send_data(DELETE_KEY, key)
                    logging.info(
                        f"Clave '{key}' borrada replicada en {succ1.ip} y {succ2.ip}"
                    )
                except Exception as e:
                    logging.error(
                        f"Error replicando el borrado de la clave '{key}': {e}"
                    )
        else:
            logging.info(
                f"Redirigiendo borrado de clave '{key}' al nodo primario {primary_node.ip}"
            )
            primary_node.delete_key(key)

    async def get_all_keys(self) -> List[str]:
        keys = []

        async def _get_all():
            async with get_db() as session:
                for table, Model in TABLE_MAP.items():
                    result = await session.execute(select(Model.id))
                    for id in result.scalars().all():
                        keys.append(f"{table}:{id}")

        await _get_all()
        logging.info(f"Recuperando claves desde {self.ip}: {keys}")
        return keys

    async def transfer_keys_to(self, new_node: "ChordNodeReference"):
        logging.info(f"Iniciando transferencia de llaves a {new_node.ip}")
        keys_to_transfer = []
        tables = [
            "users",
            "events",
            "group_hierarchy",
            "groups",
            "user_event",
            "member",
            "notification",
        ]

        async def _transfer():
            async with get_db() as session:
                for table in tables:
                    Model = TABLE_MAP.get(table)
                    if not Model:
                        continue
                    result = await session.execute(select(Model))
                    for row in result.scalars().all():
                        key = f"{table}:{row.id}"
                        key_hash = getShaRepr(key)
                        primary = self.find_succ(key_hash)
                        if primary.id == new_node.id:
                            data = {}
                            for k, v in row.__dict__.items():
                                if not k.startswith("_"):
                                    if isinstance(v, datetime):
                                        data[k] = v.isoformat()
                                    else:
                                        data[k] = v
                            
                            keys_to_transfer.append(
                                {"key": key, "value": json.dumps(data)}
                            )
            return keys_to_transfer

        keys_to_transfer = await _transfer()
        logging.info(f"keys_to_transfer data found: {keys_to_transfer}")
        if keys_to_transfer:
            try:
                payload = {"keys": keys_to_transfer}
                url = f"http://{new_node.ip}:5000/receive_keys"
                logging.info(
                    f"Enviando {len(keys_to_transfer)} llaves a {new_node.ip} vía REST"
                )
                response = requests.post(url, json=payload, timeout=5)
                if response.status_code == 200:
                    logging.info(f"Transferencia de llaves a {new_node.ip} completada")
                else:
                    logging.error(
                        f"Error en la transferencia de llaves: {response.status_code}"
                    )
            except Exception as e:
                logging.error(f"Error transfiriendo llaves al nuevo nodo: {e}")

    async def refresh_replication(self):
        async def _refresh():
            keys = []
            async with get_db() as session:
                for table, Model in TABLE_MAP.items():
                    result = await session.execute(select(Model.id))
                    for id in result.scalars().all():
                        keys.append(f"{table}:{id}")
            return keys

        keys = await _refresh()
        for key in keys:
            key_hash = getShaRepr(key)
            if self.find_succ(key_hash).id == self.id:
                try:
                    succ1 = self.succ
                    succ2 = succ1.succ
                    value = await self.retrieve_key(key)
                    succ1._send_data(REPLICATE_KEY, f"{key},{value}")
                    succ2._send_data(REPLICATE_KEY, f"{key},{value}")
                    logging.info(
                        f"Refrescada replicación de '{key}' en {succ1.ip} y {succ2.ip}"
                    )
                except Exception as e:
                    logging.error(f"Error refrescando replicación para '{key}': {e}")

    async def refresh_replication_loop(self):
        while True:
            await self.refresh_replication()
            time.sleep(60)

    def start_server(self):
        logging.info(f"Iniciando servidor en {self.ip}:{self.port}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.port))
            s.listen(10)
            while True:
                try:
                    conn, addr = s.accept()
                    logging.info(f"Conexión aceptada de {addr}")
                    threading.Thread(
                        target=self.handle_connection, args=(conn,), daemon=True
                    ).start()
                except Exception as e:
                    logging.error(f"Error aceptando conexión: {e}")

    def handle_connection(self, conn):
        try:
            data = conn.recv(4096).decode().split(DELIMITER)
            if not data:
                return
            option = int(data[0])
            response = b""
            if option == FIND_SUCCESSOR:
                id = int(data[1])
                node_ref = self.find_succ(id)
                response = f"{node_ref.id},{node_ref.ip}".encode()
            elif option == FIND_PREDECESSOR:
                id = int(data[1])
                node_ref = self.find_pred(id)
                response = f"{node_ref.id},{node_ref.ip}".encode()
            elif option == GET_SUCCESSOR:
                node_ref = self.succ if self.succ else self.ref
                response = f"{node_ref.id},{node_ref.ip}".encode()
            elif option == GET_PREDECESSOR:
                node_ref = self.pred if self.pred else self.ref
                response = f"{node_ref.id},{node_ref.ip}".encode()
            elif option == NOTIFY:
                id = int(data[1])
                ip = data[2]
                logging.info(f"handle_connection: NOTIFY recibido de {ip}")
                asyncio.run(self.notify(ChordNodeReference(ip, self.port)))
                response = b""
            elif option == CHECK_PREDECESSOR:
                self.check_predecessor()
                response = b""
            elif option == CLOSEST_PRECEDING_FINGER:
                id = int(data[1])
                node_ref = self.closest_preceding_finger(id)
                response = f"{node_ref.id},{node_ref.ip}".encode()
            elif option == STORE_KEY:
                key, value = data[1], data[2]
                logging.info(f"handle_connection: STORE_KEY para '{key}'")
                self.store_key(key, value)
                response = b""
            elif option == RETRIEVE_KEY:
                key = data[1]
                logging.info(f"handle_connection: RETRIEVE_KEY para '{key}'")
                value = asyncio.run(self.retrieve_key(key))
                response = value.encode() if value else b""
            elif option == REPLICATE_KEY:
                key, value = data[1], data[2]
                logging.info(f"handle_connection: REPLICATE_KEY para '{key}'")
                self.store_key(key, value, replica=True)
                response = b""
            elif option == GET_ALL_KEYS:
                logging.info("handle_connection: GET_ALL_KEYS")
                asyncio.run(self.get_all_keys())
                response = b""
            elif option == DELETE_KEY:
                key = data[1]
                logging.info(f"handle_connection: DELETE_KEY para '{key}'")
                asyncio.run(self.delete_key(key, replicate=True))
                response = b""
            elif option == GET_ALL_FILTERED:
                query_payload = data[1] if len(data) > 1 else "{}"
                result_json = asyncio.run(self._handle_get_all_filtered(query_payload))
                response = result_json.encode()
            conn.sendall(response)
        except Exception as e:
            logging.error(f"Error en handle_connection: {e}")
        finally:
            conn.close()
