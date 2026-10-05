from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from app.db import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Country, JobTitle  # noqa: E402


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(engine)

    with TestingSession() as session:
        session.add_all(
            [
                Country(code="IN", name="India", currency_code="INR"),
                Country(code="US", name="United States", currency_code="USD"),
            ]
        )
        session.add_all(
            [
                JobTitle(id=1, name="Software Engineer"),
                JobTitle(id=2, name="Senior Software Engineer"),
                JobTitle(id=3, name="Engineering Manager"),
            ]
        )
        session.commit()
        yield session
    engine.dispose()


@pytest.fixture()
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def employee_payload() -> dict:
    return {
        "employee_code": "EMP-0001",
        "full_name": "Aryan Agrawal",
        "job_title_id": 1,
        "country_code": "IN",
        "salary": "1800000.00",
        "department": "Engineering",
        "employment_status": "active",
        "hired_at": "2023-08-01",
    }
