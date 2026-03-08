import asyncio
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from core.database import Base

# Import all models so they register with Base.metadata (required for autogenerate)
from modules.auth import models as _auth_models  # noqa: F401

target_metadata = Base.metadata
DATABASE_URL = context.config.get_main_option("sqlalchemy.url")

def run_migrations_offline():
    """Offline migrations."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Online migrations using Async engine."""
    async def do_run():
        engine = create_async_engine(DATABASE_URL, poolclass=None)

        async with engine.begin() as conn:
            # Configure context with sync connection
            await conn.run_sync(lambda sync_conn: context.configure(
                connection=sync_conn,
                target_metadata=target_metadata
            ))
            # Run migrations (no connection object passed)
            await conn.run_sync(lambda sync_conn: context.run_migrations())

    asyncio.run(do_run())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()