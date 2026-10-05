from fastapi.testclient import TestClient


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
