import os
import asyncio
from alembic import context
from dotenv import load_dotenv
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection, AsyncEngine
from sqlalchemy import pool, engine_from_config

from app.infrastructure.sqlite.tables import Base
from app.settings import settings

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./database.sql')

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
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable: AsyncEngine = create_async_engine(
        config.get_main_option('sqlalchemy.url'),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

def do_run_migrations(connection: AsyncConnection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()

# Ejecutar migraciones
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

# def run_migrations_online() -> None:
#     """Run migrations in 'online' mode."""
#     # Usa engine_from_config para conexiones síncronas
#     connectable = engine_from_config(
#         config.get_section(config.config_ini_section),
#         prefix="sqlalchemy.",
#         poolclass=pool.NullPool,
#     )

#     with connectable.connect() as connection:
#         context.configure(
#             connection=connection, 
#             target_metadata=target_metadata
#         )

#         with context.begin_transaction():
#             context.run_migrations()

# Elimina la parte asíncrona
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()