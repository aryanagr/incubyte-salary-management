from decimal import Decimal


def test_create_employee_returns_normalized_record(client, employee_payload):
    response = client.post("/api/v1/employees", json=employee_payload)

    assert response.status_code == 201
    body = response.json()
    assert body["employee_code"] == "EMP-0001"
    assert body["full_name"] == "Aryan Agrawal"
    assert body["country"]["code"] == "IN"
    assert body["country"]["currency_code"] == "INR"
    assert body["job_title"]["name"] == "Software Engineer"
    assert Decimal(body["salary"]) == Decimal("1800000.00")


def test_create_employee_rejects_non_positive_salary(client, employee_payload):
    employee_payload["salary"] = "0"
    response = client.post("/api/v1/employees", json=employee_payload)
    assert response.status_code == 422


def test_create_employee_rejects_unknown_reference_values(client, employee_payload):
    employee_payload["country_code"] = "ZZ"
    response = client.post("/api/v1/employees", json=employee_payload)
    assert response.status_code == 422


def test_duplicate_employee_code_is_conflict(client, employee_payload):
    assert client.post("/api/v1/employees", json=employee_payload).status_code == 201
    response = client.post("/api/v1/employees", json=employee_payload)
    assert response.status_code == 409


def test_employee_crud_flow(client, employee_payload):
    created = client.post("/api/v1/employees", json=employee_payload).json()
    employee_id = created["id"]

    read = client.get(f"/api/v1/employees/{employee_id}")
    assert read.status_code == 200

    updated = client.patch(
        f"/api/v1/employees/{employee_id}",
        json={"salary": "2000000.50", "job_title_id": 2},
    )
    assert updated.status_code == 200
    assert updated.json()["salary"] == "2000000.50"
    assert updated.json()["job_title"]["id"] == 2

    deleted = client.delete(f"/api/v1/employees/{employee_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/employees/{employee_id}").status_code == 404
    assert client.delete(f"/api/v1/employees/{employee_id}").status_code == 204


def test_list_is_paginated_filterable_searchable_and_sortable(client, employee_payload):
    records = [
        ("EMP-0001", "Alice Rao", "1800000.00", 1, "IN", "Engineering"),
        ("EMP-0002", "Bob Shah", "2200000.00", 2, "IN", "Engineering"),
        ("EMP-0003", "Charlie Smith", "120000.00", 1, "US", "Engineering"),
    ]
    for code, name, salary, title_id, country, department in records:
        payload = employee_payload | {
            "employee_code": code,
            "full_name": name,
            "salary": salary,
            "job_title_id": title_id,
            "country_code": country,
            "department": department,
        }
        assert client.post("/api/v1/employees", json=payload).status_code == 201

    response = client.get(
        "/api/v1/employees",
        params={
            "page": 1,
            "page_size": 1,
            "country_code": "IN",
            "search": "bob",
            "sort_by": "salary",
            "sort_dir": "desc",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["page"] == 1
    assert body["page_size"] == 1
    assert body["pages"] == 1
    assert [item["employee_code"] for item in body["items"]] == ["EMP-0002"]


def test_list_page_size_has_hard_limit(client):
    response = client.get("/api/v1/employees", params={"page_size": 501})
    assert response.status_code == 422


def test_patch_rejects_null_for_required_employee_fields(client, employee_payload):
    created = client.post("/api/v1/employees", json=employee_payload).json()
    for field in ["employee_code", "full_name", "job_title_id", "country_code", "salary", "department", "employment_status"]:
        response = client.patch(f"/api/v1/employees/{created['id']}", json={field: None})
        assert response.status_code == 422, field


def test_create_normalizes_whitespace_and_allows_duplicate_names(client, employee_payload):
    first = client.post(
        "/api/v1/employees",
        json=employee_payload | {"employee_code": " D-1 ", "full_name": "  Maya   Rao  ", "department": "  Engineering  "},
    )
    second = client.post(
        "/api/v1/employees",
        json=employee_payload | {"employee_code": "D-2", "full_name": "Maya Rao"},
    )
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["employee_code"] == "D-1"
    assert first.json()["full_name"] == "Maya Rao"
    assert first.json()["department"] == "Engineering"


def test_page_beyond_end_is_empty_but_preserves_total(client, employee_payload):
    assert client.post("/api/v1/employees", json=employee_payload).status_code == 201
    response = client.get("/api/v1/employees", params={"page": 99, "page_size": 20})
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 1
    assert body["pages"] == 1


def test_delete_soft_deletes_employee_but_hides_from_current_views(client, db, employee_payload):
    from sqlalchemy import func, select
    from app.models import Employee

    created = client.post('/api/v1/employees', json=employee_payload)
    assert created.status_code == 201
    employee_id = created.json()['id']

    deleted = client.delete(f'/api/v1/employees/{employee_id}')
    assert deleted.status_code == 204

    # Product view behaves like deletion.
    assert client.get(f'/api/v1/employees/{employee_id}').status_code == 404
    listing = client.get('/api/v1/employees').json()
    assert listing['total'] == 0

    # Storage retains the HR record for traceability.
    assert db.scalar(select(func.count()).select_from(Employee)) == 1
    stored = db.get(Employee, employee_id)
    assert stored is not None
    assert stored.deleted_at is not None

    # HTTP DELETE remains safe to repeat even though the record is already hidden.
    assert client.delete(f'/api/v1/employees/{employee_id}').status_code == 204
