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
