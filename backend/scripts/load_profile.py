from __future__ import annotations

import asyncio
import os
import statistics
import tempfile
import time
from collections.abc import Generator
from pathlib import Path

import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Configure safe local settings before importing the application.
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("AUTH_SECRET", "load-profile-local-secret")

from app.db import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import seed_employees  # noqa: E402

REQUEST_COUNT = 160
CONCURRENCY = 8
P95_LIMIT_MS = 1000.0


async def main() -> None:
    with tempfile.TemporaryDirectory(prefix="salary-load-") as temp_dir:
        db_path = Path(temp_dir) / "load.db"
        engine = create_engine(
            f"sqlite+pysqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
        )
        SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
        Base.metadata.create_all(engine)

        data_dir = Path(__file__).resolve().parents[1] / "data"
        with SessionLocal() as seed_db:
            started = time.perf_counter()
            result = seed_employees(
                seed_db,
                count=10_000,
                first_names_path=data_dir / "first_names.txt",
                last_names_path=data_dir / "last_names.txt",
                batch_size=1_000,
            )
            seed_seconds = time.perf_counter() - started
            assert result.processed == 10_000

        def override_get_db() -> Generator[Session, None, None]:
            with SessionLocal() as session:
                yield session

        app.dependency_overrides[get_db] = override_get_db
        transport = httpx.ASGITransport(app=app)
        limits = httpx.Limits(max_connections=CONCURRENCY, max_keepalive_connections=CONCURRENCY)
        latencies: list[float] = []

        try:
            async with httpx.AsyncClient(transport=transport, base_url="http://load", limits=limits) as client:
                login = await client.post(
                    "/api/v1/auth/login",
                    json={"email": "manager@salary.demo", "password": "Manager@123"},
                )
                assert login.status_code == 200

                paths = [
                    "/api/v1/employees?page=1&page_size=20&sort_by=full_name&sort_dir=asc",
                    "/api/v1/employees?page=5&page_size=20&country_code=IN",
                    "/api/v1/employees?page=1&page_size=20&search=EMP-00",
                    "/api/v1/insights/countries/IN",
                ]
                semaphore = asyncio.Semaphore(CONCURRENCY)

                async def one_request(index: int) -> None:
                    async with semaphore:
                        started = time.perf_counter()
                        response = await client.get(paths[index % len(paths)])
                        elapsed_ms = (time.perf_counter() - started) * 1000
                        assert response.status_code == 200, (response.status_code, response.text[:200])
                        latencies.append(elapsed_ms)

                await asyncio.gather(*(one_request(index) for index in range(REQUEST_COUNT)))
        finally:
            app.dependency_overrides.clear()
            engine.dispose()

        ordered = sorted(latencies)
        p50 = statistics.median(ordered)
        p95 = ordered[max(0, int(len(ordered) * 0.95) - 1)]
        average = statistics.mean(ordered)

        print(
            f"10k profile: seed={seed_seconds:.3f}s requests={REQUEST_COUNT} concurrency={CONCURRENCY} "
            f"avg={average:.1f}ms p50={p50:.1f}ms p95={p95:.1f}ms"
        )
        if p95 > P95_LIMIT_MS:
            raise SystemExit(
                f"Load-profile regression: p95 {p95:.1f}ms exceeded bounded CI guard {P95_LIMIT_MS:.0f}ms"
            )


if __name__ == "__main__":
    asyncio.run(main())
