from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth
from app.infrastructure.db.session import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

# TODO: Move middlewares to other files

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Ajusta el origen para el frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluye las rutas
app.include_router(auth.router, prefix="/api/users", tags=["users"])

@app.get("/api/healthcheck")
def healthcheck():
    return {"message": "API is running!"}
