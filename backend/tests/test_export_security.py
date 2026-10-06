from fastapi.testclient import TestClient


def test_export_status_and_dispatch_are_private_to_requester(raw_client: TestClient):
    raw_client.post(
        "/api/v1/auth/login",
        json={"email": "manager@salary.demo", "password": "Manager@123"},
    )
    queued = raw_client.post(
        "/api/v1/exports",
        json={"recipient_email": "manager@example.com"},
    )
    assert queued.status_code == 202
    job_id = queued.json()["id"]

    raw_client.post("/api/v1/auth/logout")
    raw_client.post(
        "/api/v1/auth/login",
        json={"email": "hr@salary.demo", "password": "Hr@123"},
    )

    assert raw_client.get(f"/api/v1/exports/{job_id}").status_code == 404
    assert raw_client.post(f"/api/v1/exports/{job_id}/dispatch").status_code == 404


def test_export_queue_requires_authentication(raw_client: TestClient):
    response = raw_client.post(
        "/api/v1/exports",
        json={"recipient_email": "reviewer@example.com"},
    )
    assert response.status_code == 401


def test_recovery_worker_requires_matching_cron_secret(raw_client: TestClient, monkeypatch):
    secret = "test-" + "cron-secret"
    monkeypatch.setenv("CRON_SECRET", secret)

    assert raw_client.get("/api/internal/export-jobs/process").status_code == 401
    assert raw_client.get(
        "/api/internal/export-jobs/process",
        headers={"Authorization": "Bearer wrong-secret"},
    ).status_code == 401
    assert raw_client.get(
        "/api/internal/export-jobs/process",
        headers={"Authorization": f"Bearer {secret}"},
    ).status_code == 200
