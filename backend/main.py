import inject
from fastapi import FastAPI

from app.settings import configure as inject_configure
from app.api.user_router import router as user_router
from app.api.auth_router import router as auth_router
from app.api.event_router import router as event_router
from app.infrastructure.sqlite.tables import Base
from app.infrastructure.sqlite.database import engine


app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


inject.configure(inject_configure)

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(event_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
