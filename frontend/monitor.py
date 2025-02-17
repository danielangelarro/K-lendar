import socket
import os
import asyncio
import threading
import websockets

# Configuración de variables
MULTICAST_GROUP = "224.0.0.1"  
PROXY_MULTICAST_PORT = 10000   
DELIMITER = "<<DELIM>>"        
ENV_FILE = ".env"
WEBSOCKET_HOST = "0.0.0.0"  # Acepta conexiones en cualquier interfaz
WEBSOCKET_PORT = 8765  # Puerto WebSocket

# Lista de clientes WebSocket conectados
connected_clients = set()

async def websocket_handler(websocket, path=None):
    """Maneja las conexiones WebSocket entrantes."""
    connected_clients.add(websocket)
    print(f"Cliente WebSocket conectado: {websocket.remote_address}")
    
    try:
        await websocket.wait_closed()
    except Exception as e:
        print(f"Error en WebSocket: {e}")
    finally:
        connected_clients.remove(websocket)
        print(f"Cliente WebSocket desconectado: {websocket.remote_address}")

async def send_to_clients(message):
    """Envía un mensaje a todos los clientes WebSocket conectados."""
    if connected_clients:
        print("Enviando mensaje a :", connected_clients)
        await asyncio.gather(*[ws.send(message) for ws in connected_clients])

async def multicast_listener():
    """Escucha mensajes multicast y los procesa."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", PROXY_MULTICAST_PORT))

    mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton("0.0.0.0")
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f"Escuchando en el grupo multicast {MULTICAST_GROUP}:{PROXY_MULTICAST_PORT}...")

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            data = data.decode().strip()
            print(f"Datos recibidos: {data}")

            if DELIMITER in data:
                # node_ip, node_port = data.split(DELIMITER)
                node_ip, node_port = data.split(DELIMITER)

                # Enviar información a los clientes WebSocket
                message = f"NODE_IP={node_ip}, NODE_PORT={node_port}"
                await send_to_clients(message)

                print(f"Descubierto nodo: {node_ip}:{node_port} [message]: {message}")
            else:
                print(f"Error: Datos en formato incorrecto: {data}")

        except Exception as e:
            print(f"Error en la recepción de datos: {e}")

def run_multicast_listener():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(multicast_listener())

async def main():
    """Inicia los servicios de multicast y WebSocket en paralelo."""
    websocket_server = websockets.serve(websocket_handler, WEBSOCKET_HOST, WEBSOCKET_PORT)
    await asyncio.gather(websocket_server)
    await asyncio.Future() 

if __name__ == "__main__":
    threading.Thread(target=run_multicast_listener, daemon=True).start()
    asyncio.run(main())
