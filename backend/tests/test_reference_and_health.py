def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_reference_data(client):
    response = client.get("/api/v1/reference-data")
    assert response.status_code == 200
    body = response.json()
    assert {c["code"] for c in body["countries"]} == {"IN", "US"}
    assert {j["name"] for j in body["job_titles"]} >= {"Software Engineer", "Engineering Manager"}
