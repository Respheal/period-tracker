from fastapi.testclient import TestClient


def test_create_user_success(client: TestClient) -> None:
    response = client.post("/users/", params={"name": "Alice"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alice"
    assert "id" in data
