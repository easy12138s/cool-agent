from fastapi.testclient import TestClient

from src.api.run import app


client = TestClient(app)


def test_health() -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "environment" in data


def test_echo() -> None:
    resp = client.post("/api/v1/echo", json={"message": "hello"})
    assert resp.status_code == 200
    assert resp.json() == {"message": "hello"}


def test_ws_echo() -> None:
    with client.websocket_connect("/api/v1/ws") as ws:
        ws.send_text("ping")
        assert ws.receive_text() == "ping"
