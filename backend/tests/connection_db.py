import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

# Obtener la URL de la base de datos
database_url = os.getenv('DATABASE_URL')

async def test_connection():
    # Crear el motor de SQLAlchemy para conexiones asíncronas
    engine = create_async_engine(database_url, echo=True)

    # Crear una sesión asíncrona
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Probar la conexión
    async with async_session() as session:
        async with session.begin():
            print("Conexión exitosa a la base de datos.")

# Ejecutar la función de prueba de conexión
asyncio.run(test_connection())