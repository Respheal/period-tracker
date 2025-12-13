from fastapi.testclient import TestClient

from api.utils.config import Settings


def test_read_root(client: TestClient, settings: Settings) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
