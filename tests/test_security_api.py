from fastapi.testclient import TestClient
from project_name import app


def test_user_login_no_username_match():
    client = TestClient(app)
    response = client.post(
        "/token",
        data={"username": "doesNotExist", "password": "doesNotExist"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401


def test_user_login_no_password_match():
    client = TestClient(app)
    response = client.post(
        "/token",
        data={"username": "admin", "password": "incorrect password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401


def test_secure_api_malformed_headers():
    client = TestClient(app)
    token = client.post(
        "/token",
        data={"username": "admin", "password": "admin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    ).json()["access_token"]
    malformed_token = token[:5] + "a" + token[5:]
    client.headers["Authorization"] = f"Bearer {malformed_token}"
    response = client.get("/user/me")
    assert response.status_code == 401
