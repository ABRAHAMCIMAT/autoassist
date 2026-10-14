import os

os.environ["DATABASE_URL"] = "sqlite:///./test_autoassist.db"
os.environ["KNOWLEDGE_DIR"] = "../knowledge"

from fastapi.testclient import TestClient

from app.main import app


def test_health():
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"


def test_warranty_lookup():
    with TestClient(app) as client:
        response = client.post(
            "/api/chat",
            json={"message": "¿Mi vehículo 3D6AA5CG1BG000001 tiene garantía?"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["intent"] == "garantia"
        assert body["escalated"] is False
        assert "2027-02-14" in body["answer"]


def test_explicit_handoff_contains_evidence():
    with TestClient(app) as client:
        chat = client.post("/api/chat", json={"message": "Quiero hablar con una persona"})
        assert chat.json()["escalated"] is True
        queue = client.get("/api/escalations").json()
        assert queue[0]["evidence"]["conversation"]
