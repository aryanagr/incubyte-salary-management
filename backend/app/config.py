from __future__ import annotations

import os


def normalize_database_url(value: str) -> str:
    """Normalize common Postgres URLs to SQLAlchemy's psycopg v3 dialect."""
    if value.startswith("postgres://"):
        return value.replace("postgres://", "postgresql+psycopg://", 1)
    if value.startswith("postgresql://"):
        return value.replace("postgresql://", "postgresql+psycopg://", 1)
    return value


class Settings:
    def __init__(self) -> None:
        self.database_url = normalize_database_url(
            os.getenv("DATABASE_URL", "sqlite+pysqlite:///./salary_management.db")
        )
        self.cors_origins = tuple(
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
            if origin.strip()
        )


settings = Settings()
