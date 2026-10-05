from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import func, select, text

from .db import SessionLocal, engine
from .models import Employee
from .seed import seed_employees


BOOTSTRAP_LOCK_KEY = 72619431


def bootstrap_database() -> dict[str, int | float]:
    """Apply migrations and seed the deterministic assessment dataset once.

    This is intended only for a controlled first-deploy bootstrap. The HTTP
    route that calls it is token-gated and disabled when BOOTSTRAP_TOKEN is
    absent. A PostgreSQL advisory lock prevents concurrent bootstrap requests.
    """
    backend_root = Path(__file__).resolve().parents[1]
    alembic_config = Config(str(backend_root / "alembic.ini"))

    lock_connection = engine.connect()
    is_postgres = lock_connection.dialect.name == "postgresql"
    try:
        if is_postgres:
            lock_connection.execute(
                text("SELECT pg_advisory_lock(:key)"),
                {"key": BOOTSTRAP_LOCK_KEY},
            )

        command.upgrade(alembic_config, "head")
        with SessionLocal() as db:
            result = seed_employees(
                db,
                count=10_000,
                first_names_path=backend_root / "data" / "first_names.txt",
                last_names_path=backend_root / "data" / "last_names.txt",
                batch_size=1_000,
            )
            physical_count = int(db.scalar(select(func.count()).select_from(Employee)) or 0)
        return {
            "processed": result.processed,
            "physical_count": physical_count,
            "elapsed_seconds": round(result.elapsed_seconds, 3),
        }
    finally:
        if is_postgres:
            lock_connection.execute(
                text("SELECT pg_advisory_unlock(:key)"),
                {"key": BOOTSTRAP_LOCK_KEY},
            )
        lock_connection.close()
