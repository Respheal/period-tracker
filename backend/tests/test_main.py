from fastapi.testclient import TestClient

from api.utils.config import Settings


def test_read_root(client: TestClient, settings: Settings) -> None:
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "test" in data["app_name"]
    assert data["app_name"] == settings.APP_NAME
    assert data["version"] == settings.APP_VERSION
