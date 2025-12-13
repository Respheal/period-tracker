from fastapi.testclient import TestClient


def test_create_user_success(client: TestClient) -> None:
    response = client.post(
        "/users/", json={"username": "Alice", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "Alice"
