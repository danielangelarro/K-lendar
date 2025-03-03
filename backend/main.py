import json
import socket
import threading
from fastapi.responses import JSONResponse
import inject
import asyncio
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.settings import configure as inject_configure
from app.api.user_router import router as user_router
from app.api.auth_router import router as auth_router
from app.api.chord_router import router as chord_router
from app.api.event_router import router as event_router
from app.api.group_router import router as group_router
from app.api.agenda_router import router as agenda_router
from app.api.member_router import router as member_router
from app.api.invitation_router import router as invitation_router
from app.api.notification_router import router as notification_router
from app.infrastructure.sqlite.tables import Base
from app.infrastructure.sqlite.database import get_engine
from app.settings import settings


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

# app.add_middleware(LoggingMiddleware)


@app.on_event("startup")
async def startup():
    threading.Thread(target=settings.chord_service.start, daemon=True).start()
    engine = get_engine()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/ping")
def ping():
    return {"status": "ok"}


inject.configure(inject_configure)

# Routes
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(chord_router)
app.include_router(event_router)
app.include_router(group_router)
app.include_router(member_router)
app.include_router(agenda_router)
app.include_router(invitation_router)
app.include_router(notification_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.IP, port=settings.PORT)
