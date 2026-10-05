def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_database_readiness(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_reference_data(client):
    response = client.get("/api/v1/reference-data")
    assert response.status_code == 200
    body = response.json()
    assert {c["code"] for c in body["countries"]} == {"IN", "US"}
    assert {j["name"] for j in body["job_titles"]} >= {"Software Engineer", "Engineering Manager"}
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["pragma"] == "no-cache"
