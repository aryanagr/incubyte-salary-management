from decimal import Decimal


def add_employee(client, payload, *, code, name, salary, title_id=1, country="IN"):
    response = client.post(
        "/api/v1/employees",
        json=payload
        | {
            "employee_code": code,
            "full_name": name,
            "salary": str(salary),
            "job_title_id": title_id,
            "country_code": country,
        },
    )
    assert response.status_code == 201


def test_country_insights_are_mathematically_correct(client, employee_payload):
    add_employee(client, employee_payload, code="E1", name="A", salary="100.00", title_id=1)
    add_employee(client, employee_payload, code="E2", name="B", salary="200.00", title_id=1)
    add_employee(client, employee_payload, code="E3", name="C", salary="600.00", title_id=2)
    add_employee(client, employee_payload, code="E4", name="US", salary="1000.00", title_id=1, country="US")

    response = client.get("/api/v1/insights/countries/IN")
    assert response.status_code == 200
    body = response.json()
    assert body["employee_count"] == 3
    assert Decimal(body["min_salary"]) == Decimal("100.00")
    assert Decimal(body["max_salary"]) == Decimal("600.00")
    assert Decimal(body["average_salary"]) == Decimal("300.00")
    assert Decimal(body["total_payroll"]) == Decimal("900.00")
    assert body["highest_paid_employee"]["employee_code"] == "E3"
    assert body["lowest_paid_employee"]["employee_code"] == "E1"

    breakdown = {row["job_title"]["name"]: row for row in body["job_titles"]}
    assert breakdown["Software Engineer"]["employee_count"] == 2
    assert Decimal(breakdown["Software Engineer"]["average_salary"]) == Decimal("150.00")


def test_job_title_average_is_scoped_to_country(client, employee_payload):
    add_employee(client, employee_payload, code="IN1", name="A", salary="100", title_id=1, country="IN")
    add_employee(client, employee_payload, code="IN2", name="B", salary="300", title_id=1, country="IN")
    add_employee(client, employee_payload, code="US1", name="C", salary="9999", title_id=1, country="US")

    response = client.get("/api/v1/insights/countries/IN/job-titles/1")
    assert response.status_code == 200
    body = response.json()
    assert body["employee_count"] == 2
    assert Decimal(body["average_salary"]) == Decimal("200.00")


def test_empty_country_returns_stable_empty_insight(client):
    response = client.get("/api/v1/insights/countries/US")
    assert response.status_code == 200
    body = response.json()
    assert body["employee_count"] == 0
    assert body["min_salary"] is None
    assert body["max_salary"] is None
    assert body["average_salary"] is None
    assert body["total_payroll"] == "0.00"


def test_insights_change_after_salary_update_and_delete(client, employee_payload):
    add_employee(client, employee_payload, code="X1", name="A", salary="100", title_id=1, country="IN")
    add_employee(client, employee_payload, code="X2", name="B", salary="300", title_id=1, country="IN")

    listing = client.get("/api/v1/employees", params={"search": "X1"}).json()
    employee_id = listing["items"][0]["id"]
    assert client.patch(f"/api/v1/employees/{employee_id}", json={"salary": "500"}).status_code == 200

    insight = client.get("/api/v1/insights/countries/IN").json()
    assert Decimal(insight["average_salary"]) == Decimal("400.00")
    assert Decimal(insight["max_salary"]) == Decimal("500.00")

    assert client.delete(f"/api/v1/employees/{employee_id}").status_code == 204
    insight = client.get("/api/v1/insights/countries/IN").json()
    assert insight["employee_count"] == 1
    assert Decimal(insight["average_salary"]) == Decimal("300.00")


def test_money_aggregates_have_stable_two_decimal_serialization(client, employee_payload):
    add_employee(client, employee_payload, code="M1", name="A", salary="100.00", title_id=1, country="IN")
    add_employee(client, employee_payload, code="M2", name="B", salary="101.00", title_id=1, country="IN")
    body = client.get("/api/v1/insights/countries/IN").json()
    assert body["average_salary"] == "100.50"
    assert body["min_salary"] == "100.00"
    assert body["max_salary"] == "101.00"
    assert body["total_payroll"] == "201.00"
