def test_user_list(api_client_authenticated):
    response = api_client_authenticated.get("/user/")
    assert response.status_code == 200
    result = response.json()
    assert "admin" in result[0]["username"]


def test_user_create(api_client_authenticated):
    response = api_client_authenticated.post(
        "/user/",
        json={
            "username": "foo",
            "password": "bar",
            "superuser": False,
            "disabled": False,
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert result["username"] == "foo"
