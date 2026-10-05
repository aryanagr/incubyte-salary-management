import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.employee_exports import build_employee_export_csv, process_export_job_in_session
from app.export_queue import enqueue_employee_export
from app.models import EmployeeExportJob


@pytest.fixture(autouse=True)
def stub_export_queue(monkeypatch):
    async def fake_enqueue(job_id: str) -> str:
        return f"queue-message-{job_id}"

    monkeypatch.setattr("app.main.enqueue_employee_export", fake_enqueue)


def test_manager_can_queue_filtered_employee_export(client: TestClient):
    response = client.post(
        "/api/v1/exports/employees",
        json={
            "recipient_email": "reviewer@example.com",
            "search": "Aryan",
            "country_code": "IN",
            "job_title_id": 1,
            "sort_by": "full_name",
            "sort_dir": "desc",
        },
    )

    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "queued"
    assert body["recipient_email"] == "reviewer@example.com"
    assert body["filters"] == {
        "search": "Aryan",
        "country_code": "IN",
        "job_title_id": 1,
        "sort_by": "full_name",
        "sort_dir": "desc",
    }
    assert body["id"]

    status_response = client.get(f"/api/v1/exports/employees/{body['id']}")
    assert status_response.status_code == 200
    assert status_response.json()["id"] == body["id"]


def test_hr_staff_cannot_queue_salary_export(raw_client: TestClient):
    login = raw_client.post(
        "/api/v1/auth/login",
        json={"email": "hr@salary.demo", "password": "Hr@123"},
    )
    assert login.status_code == 200

    response = raw_client.post(
        "/api/v1/exports/employees",
        json={"recipient_email": "reviewer@example.com"},
    )
    assert response.status_code == 403


def test_export_request_validates_recipient_email(client: TestClient):
    response = client.post(
        "/api/v1/exports/employees",
        json={"recipient_email": "not-an-email"},
    )
    assert response.status_code == 422


def test_export_csv_matches_current_directory_filters(client: TestClient, db: Session, employee_payload: dict):
    first = client.post("/api/v1/employees", json=employee_payload)
    assert first.status_code == 201

    other_country = {
        **employee_payload,
        "employee_code": "EMP-0002",
        "full_name": "Aryan Other Country",
        "country_code": "US",
        "salary": "120000.00",
    }
    assert client.post("/api/v1/employees", json=other_country).status_code == 201

    different_name = {
        **employee_payload,
        "employee_code": "EMP-0003",
        "full_name": "Neha Sharma",
    }
    assert client.post("/api/v1/employees", json=different_name).status_code == 201

    queued = client.post(
        "/api/v1/exports/employees",
        json={
            "recipient_email": "reviewer@example.com",
            "search": "Aryan",
            "country_code": "IN",
            "job_title_id": 1,
        },
    ).json()
    job = db.get(EmployeeExportJob, queued["id"])
    assert job is not None

    csv_bytes, row_count = build_employee_export_csv(db, job)
    text = csv_bytes.decode("utf-8-sig")

    assert row_count == 1
    assert "Aryan Agrawal" in text
    assert "Aryan Other Country" not in text
    assert "Neha Sharma" not in text


def test_queue_redelivery_does_not_send_export_twice(
    client: TestClient,
    db: Session,
    employee_payload: dict,
    monkeypatch,
):
    assert client.post("/api/v1/employees", json=employee_payload).status_code == 201
    queued = client.post(
        "/api/v1/exports/employees",
        json={"recipient_email": "reviewer@example.com"},
    ).json()

    calls: list[dict] = []

    def fake_send(**kwargs):
        calls.append(kwargs)
        return "email-message-123"

    monkeypatch.setattr("app.employee_exports.send_employee_export_email", fake_send)

    process_export_job_in_session(db, queued["id"])
    process_export_job_in_session(db, queued["id"])

    job = db.get(EmployeeExportJob, queued["id"])
    assert job is not None
    assert job.status == "sent"
    assert job.row_count == 1
    assert job.attempt_count == 1
    assert job.provider_message_id == "email-message-123"
    assert len(calls) == 1


def test_export_neutralizes_spreadsheet_formula_cells(client: TestClient, db: Session, employee_payload: dict):
    malicious = {
        **employee_payload,
        "employee_code": "=CMD",
        "full_name": "=HYPERLINK(\"https://example.com\")",
        "department": "+SUM(1,1)",
    }
    created = client.post("/api/v1/employees", json=malicious)
    assert created.status_code == 201

    queued = client.post(
        "/api/v1/exports/employees",
        json={"recipient_email": "reviewer@example.com", "search": "HYPERLINK"},
    ).json()
    job = db.get(EmployeeExportJob, queued["id"])
    assert job is not None

    csv_bytes, row_count = build_employee_export_csv(db, job)
    text = csv_bytes.decode("utf-8-sig")

    assert row_count == 1
    assert "'=CMD" in text
    assert "'=HYPERLINK" in text
    assert "'+SUM" in text


def test_queue_fails_explicitly_when_runtime_is_unavailable(monkeypatch):
    monkeypatch.delenv("VERCEL", raising=False)
    monkeypatch.delenv("VERCEL_QUEUE_BASE_URL", raising=False)

    with pytest.raises(RuntimeError, match="queue is not configured"):
        asyncio.run(enqueue_employee_export("job-123"))
