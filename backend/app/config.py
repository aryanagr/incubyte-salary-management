from __future__ import annotations

import os


class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite+pysqlite:///./salary_management.db")
    cors_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    )


settings = Settings()
