import app.main as main_module


def test_bootstrap_route_is_hidden_when_token_is_not_configured(client, monkeypatch):
    monkeypatch.delenv("BOOTSTRAP_TOKEN", raising=False)
    response = client.post("/api/internal/bootstrap")
    assert response.status_code == 404


def test_bootstrap_route_rejects_wrong_token(client, monkeypatch):
    monkeypatch.setenv("BOOTSTRAP_TOKEN", "expected-secret")
    response = client.post("/api/internal/bootstrap", headers={"X-Bootstrap-Token": "wrong"})
    assert response.status_code == 403


def test_bootstrap_route_runs_with_correct_token(client, monkeypatch):
    monkeypatch.setenv("BOOTSTRAP_TOKEN", "expected-secret")
    monkeypatch.setattr(
        main_module,
        "bootstrap_database",
        lambda: {"processed": 10_000, "physical_count": 10_000, "elapsed_seconds": 1.25},
    )
    response = client.post("/api/internal/bootstrap", headers={"X-Bootstrap-Token": "expected-secret"})
    assert response.status_code == 200
    assert response.json()["physical_count"] == 10_000
