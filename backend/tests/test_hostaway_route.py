from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_get_hostaway_reviews_returns_success():
    resp = client.get("/api/reviews/hostaway")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert isinstance(data["result"], list)
    assert len(data["result"]) > 0
