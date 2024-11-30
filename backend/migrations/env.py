import os
import asyncio
from alembic import context
from dotenv import load_dotenv
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection
from sqlalchemy import pool
from app.infrastructure.sqlite.tables import Base
from app.settings import settings

load_dotenv()

# Usa la URL de base de datos asíncrona
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./database.sql')

config = context.config
config.set_main_option('sqlalchemy.url', DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    from sqlalchemy import create_engine
    
    # Usa una conexión síncrona para las migraciones
    engine = create_engine(DATABASE_URL.replace('+aiosqlite', ''))
    
    with engine.connect() as connection:
        do_run_migrations(connection)

# Decide qué función de migración ejecutar
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()