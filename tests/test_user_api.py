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


def test_get_my_profile(api_client_not_superuser):
    response = api_client_not_superuser.get("/user/me")
    assert response.status_code == 200
    result = response.json()
    assert result["username"] == "regular"
    assert result["id"] == 3


def test_get_other_profile_by_id(api_client_not_superuser):
    response = api_client_not_superuser.get("/user/1")
    assert response.status_code == 200
    result = response.json()
    assert result["username"] == "admin2"
    assert result["id"] == 1


def test_get_other_profile_by_name(api_client_not_superuser):
    response = api_client_not_superuser.get("/user/admin")
    assert response.status_code == 200
    result = response.json()
    assert result["username"] == "admin"
    assert result["id"] == 2
