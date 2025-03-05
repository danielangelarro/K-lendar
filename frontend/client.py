import os
import threading
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import socket
import asyncio
import requests
import uvicorn

app = FastAPI()

MULTICAST_GROUP = "224.0.0.1"
PROXY_MULTICAST_PORT = 10000
DELIMITER = "<<DELIM>>"
active_servers = set()


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.get("/servers")
def servers():
    return active_servers


def listen_multicast():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", PROXY_MULTICAST_PORT))
    mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton("0.0.0.0")
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        data, _ = sock.recvfrom(1024)
        message = data.decode()
        if DELIMITER in message:
            ip, port = message.split(DELIMITER)
            active_servers.add((ip, port))


def check_servers():
    while True:
        for ip, port in list(active_servers):
            port_int = int(port) - 3000
            try:
                response = requests.get(f"http://{ip}:{port_int}/ping", timeout=5)
                if response.status_code != 200:
                    active_servers.remove((ip, port))
            except requests.RequestException:
                if (ip, port) in active_servers:
                    active_servers.remove((ip, port))
        print(active_servers)
        time.sleep(10)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket client accepted")
    try:
        while True:
            if active_servers:
                # Selecciona un servidor activo (puedes mejorar la selección si es necesario)
                ip, port = next(iter(active_servers))
                port_int = int(port) - 3000
                print(f"ip: {ip} - port: {port}")
                try:
                    response = requests.get(f"http://{ip}:{port_int}/ping", timeout=5)
                    print("Response status:", response.status_code)
                    if response.status_code == 200:
                        await websocket.send_text(f"{ip}{DELIMITER}{port_int}")
                    else:
                        active_servers.discard((ip, port))
                except requests.RequestException as e:
                    print("Error al comprobar servidor:", e)
                    active_servers.discard((ip, port))
            time.sleep(10)
    except WebSocketDisconnect:
        print("WebSocket client disconnected")


@app.on_event("startup")
async def startup_event():
    threading.Thread(target=listen_multicast, daemon=True).start()
    threading.Thread(target=check_servers, daemon=True).start()


if __name__ == "__main__":
    host = socket.gethostbyname(socket.gethostname())
    port = int(os.getenv('WS_PORT', 8000))
    uvicorn.run(app, host=host, port=port)
