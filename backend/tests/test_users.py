from fastapi.testclient import TestClient


def test_create_user_success(client: TestClient) -> None:
    response = client.post(
        "/users/", json={"username": "Alice", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "Alice"


def test_read_me(client: TestClient, user_headers: dict[str, str]) -> None:
    r = client.get("/users/me", headers=user_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_admin"] is False
