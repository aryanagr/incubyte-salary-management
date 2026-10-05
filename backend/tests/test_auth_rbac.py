from fastapi.testclient import TestClient


def test_login_exposes_manager_identity(raw_client: TestClient):
    response = raw_client.post(
        "/api/v1/auth/login",
        json={"email": "manager@salary.demo", "password": "Manager@123"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "hr_manager"
    assert response.json()["name"] == "Maya Sharma"
    assert "salary_demo_session=" in response.headers["set-cookie"]


def test_invalid_login_is_rejected(raw_client: TestClient):
    response = raw_client.post(
        "/api/v1/auth/login",
        json={"email": "manager@salary.demo", "password": "wrong"},
    )
    assert response.status_code == 401


def test_protected_api_requires_login(raw_client: TestClient):
    response = raw_client.get("/api/v1/reference-data")
    assert response.status_code == 401


def test_hr_staff_can_read_but_cannot_mutate(raw_client: TestClient, employee_payload: dict):
    login = raw_client.post(
        "/api/v1/auth/login",
        json={"email": "hr@salary.demo", "password": "Hr@123"},
    )
    assert login.status_code == 200
    assert raw_client.get("/api/v1/reference-data").status_code == 200

    response = raw_client.post("/api/v1/employees", json=employee_payload)
    assert response.status_code == 403


def test_manager_can_mutate(client: TestClient, employee_payload: dict):
    response = client.post("/api/v1/employees", json=employee_payload)
    assert response.status_code == 201


def test_logout_clears_session(raw_client: TestClient):
    raw_client.post(
        "/api/v1/auth/login",
        json={"email": "manager@salary.demo", "password": "Manager@123"},
    )
    assert raw_client.get("/api/v1/auth/me").status_code == 200
    assert raw_client.post("/api/v1/auth/logout").status_code == 204
    assert raw_client.get("/api/v1/auth/me").status_code == 401
