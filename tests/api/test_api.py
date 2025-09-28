import os

from fastapi.testclient import TestClient

from src.api.main import app


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_analyze_stub_mode(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = TestClient(app)
    payload = {
        "text": "OpenAI partnered with Oscar Health to modernize medical records.",
        "mode": "stub",
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["mode"] == "stub"
    assert "selling_points" in data
    assert data["summary"]["total_questions"] >= 1


def test_analyze_live_without_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = TestClient(app)
    response = client.post(
        "/analyze",
        json={"text": "Sample", "mode": "live"},
    )
    assert response.status_code == 400
