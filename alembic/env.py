from alembic import context
from sqlalchemy import create_engine
from core.database import Base
import os

# Import all models so they register with Base.metadata (required for autogenerate)
from modules.auth import models as _auth_models  # noqa: F401
from modules.organization import models as _organization_models  # noqa: F401

target_metadata = Base.metadata

# Alembic requires a sync driver (psycopg2). Use ALEMBIC_DATABASE_URL if set,
# otherwise fall back to the app DATABASE_URL but swap asyncpg → psycopg2.
_raw_url = os.getenv(
    "ALEMBIC_DATABASE_URL",
    os.getenv("DATABASE_URL", context.config.get_main_option("sqlalchemy.url")),
)
DATABASE_URL = _raw_url.replace("postgresql+asyncpg", "postgresql+psycopg2").replace(
    "postgresql+aiopg", "postgresql+psycopg2"
)

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
    """Online migrations using sync engine."""
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        context.configure(connection=conn, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()