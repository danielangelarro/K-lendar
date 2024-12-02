import json
from fastapi.responses import JSONResponse
import inject
import asyncio
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.settings import configure as inject_configure
from app.api.user_router import router as user_router
from app.api.auth_router import router as auth_router
from app.api.event_router import router as event_router
from app.api.group_router import router as group_router
from app.api.agenda_router import router as agenda_router
from app.api.member_router import router as member_router
from app.api.invitation_router import router as invitation_router
from app.api.notification_router import router as notification_router
from app.infrastructure.sqlite.tables import Base
from app.infrastructure.sqlite.database import engine


app = FastAPI()


@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except HTTPException as http_exception:
        return JSONResponse(
            status_code=http_exception.status_code,
            content={"detail": http_exception.detail},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
        )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lista de orígenes permitidos
    allow_credentials=True,   # Permitir credenciales (cookies, autenticación)
    allow_methods=["*"],      # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],      # Permitir todos los encabezados
)



# Almacena conexiones de WebSocket
active_connections = {}

@app.websocket("/ws/notifications/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    active_connections[user_id] = websocket
    try:
        while True:
            # Espera mensajes del cliente (opcional)
            data = await websocket.receive_text()
            print(f"Mensaje recibido de {user_id}: {data}")
    except WebSocketDisconnect:
        del active_connections[user_id]
        print(f"Conexión cerrada para {user_id}")

async def send_notification(user_id: str, message: str):
    if user_id in active_connections:
        websocket = active_connections[user_id]
        await websocket.send_text(json.dumps({"message": message}))

async def notification_service():
    while True:
        # Aquí deberías implementar la lógica para verificar cambios en la base de datos
        # y enviar notificaciones a los usuarios correspondientes.
        await asyncio.sleep(10)  # Simula el tiempo de espera entre verificaciones

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(notification_service())


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


inject.configure(inject_configure)

# Routes
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(event_router)
app.include_router(group_router)
app.include_router(member_router)
app.include_router(agenda_router)
app.include_router(invitation_router)
app.include_router(notification_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
