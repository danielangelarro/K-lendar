import threading
from fastapi import FastAPI, WebSocket
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
            print(active_servers)


def check_servers():
    while True:
        for ip, port in list(active_servers):
            try:
                response = requests.get(f"http://{ip}:{port}/ping", timeout=2)
                if response.status_code != 200:
                    active_servers.remove((ip, port))
            except requests.RequestException:
                active_servers.remove((ip, port))
        # await asyncio.sleep(1)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    print(f"Client accepted")

    while True:
        if active_servers:
            print("active_servers:", active_servers)

            ip, port = next(iter(active_servers))
            port = int(port) - 3000

            print(f"ip: {ip} - port: {port}")
            try:
                response = requests.get(f"http://localhost:{port}/ping", timeout=2)

                print("Response status:", response.status.code)

                if response.status_code == 200:
                    await websocket.send_text(f"{ip}{DELIMITER}{port}")
                elif (ip, port) in active_servers:
                    active_servers.remove((ip, port))
            except requests.RequestException:
                active_servers.remove((ip, port))
        await asyncio.sleep(5)


@app.on_event("startup")
async def startup_event():
    print("Iniciando...")
    threading.Thread(target=listen_multicast, daemon=True).start()
    threading.Thread(target=check_servers, daemon=True).start()
    print("Iniciado correctamente!")
    # asyncio.create_task(listen_multicast)
    # asyncio.create_task(check_servers())


if __name__ == "__main__":
    host = socket.gethostbyname(socket.gethostname())
    uvicorn.run(app, host=host, port=8000)
