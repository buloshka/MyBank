import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# =========================
# Alembic Config
# =========================

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# =========================
# Project imports
# =========================

from app.core.config import settings
from app.core.db import Base

from app.models import db

target_metadata = Base.metadata

# =========================
# Helpers
# =========================
def get_url() -> str:
    return settings.get_db_url()

# =========================
# Offline migrations
# =========================
def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

# =========================
# Online migrations (ASYNC)
# =========================
def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        {
            "sqlalchemy.url": get_url(),
        },
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async def do_run_migrations(connection: Connection) -> None:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

    async def run() -> None:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

        await connectable.dispose()

    asyncio.run(run())

# =========================
# Entry point
# =========================
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
