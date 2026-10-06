from __future__ import annotations

import time
from pathlib import Path
from statistics import median

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.seed import seed_employees


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def _median_request_ms(client: TestClient, path: str, *, repeats: int = 5) -> float:
    warmup = client.get(path)
    assert warmup.status_code == 200

    samples: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter()
        response = client.get(path)
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert response.status_code == 200
        samples.append(elapsed_ms)
    return median(samples)


@pytest.mark.performance
def test_10k_employee_operating_bounds(client: TestClient, db: Session):
    """Catch order-of-magnitude regressions without pretending CI timing is an SLA."""
    seed_result = seed_employees(
        db,
        count=10_000,
        first_names_path=DATA_DIR / "first_names.txt",
        last_names_path=DATA_DIR / "last_names.txt",
        batch_size=1_000,
    )

    assert seed_result.processed == 10_000
    assert seed_result.elapsed_seconds < 8.0

    directory = client.get("/api/v1/employees?page=1&page_size=25")
    assert directory.status_code == 200
    assert directory.json()["total"] == 10_000

    # These intentionally generous limits are regression tripwires for the assessment's
    # 10k-row requirement, not production SLAs. They remain stable on shared CI runners.
    assert _median_request_ms(client, "/api/v1/employees?page=1&page_size=25") < 250
    assert _median_request_ms(client, "/api/v1/employees?page=1&page_size=25&search=EMP-09999") < 500
    assert _median_request_ms(client, "/api/v1/insights/countries/IN") < 250
