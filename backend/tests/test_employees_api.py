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
    assert client.delete(f"/api/v1/employees/{employee_id}").status_code == 404


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
