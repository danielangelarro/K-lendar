import inject
from fastapi import FastAPI
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lista de orígenes permitidos
    allow_credentials=True,   # Permitir credenciales (cookies, autenticación)
    allow_methods=["*"],      # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],      # Permitir todos los encabezados
)

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
