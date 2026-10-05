def test_bootstrap_post_route_is_removed(client, monkeypatch):
    monkeypatch.setenv("BOOTSTRAP_TOKEN", "legacy-secret")
    response = client.post(
        "/api/internal/bootstrap",
        headers={"X-Bootstrap-Token": "legacy-secret"},
    )
    assert response.status_code == 404


def test_bootstrap_get_route_is_removed(client, monkeypatch):
    monkeypatch.setenv("BOOTSTRAP_TOKEN", "legacy-secret")
    response = client.get("/api/internal/bootstrap-once?token=legacy-secret")
    assert response.status_code == 404
