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


def test_get_other_profile_404(api_client_not_superuser):
    response = api_client_not_superuser.get("/user/99999")
    result = response.json()
    assert response.status_code == 404


def test_change_password_404(api_client_not_superuser):
    response = api_client_not_superuser.patch(
        "/user/99999/password/",
        json={"password": "string", "password_confirm": "string"},
    )
    result = response.text
    assert response.status_code == 404


def test_change_password_unauthorised(api_client_not_superuser):
    response = api_client_not_superuser.patch(
        "/user/1/password/",
        json={"password": "string", "password_confirm": "string"},
    )
    result = response.text
    assert response.status_code == 403


def test_change_password_no_match(api_client_not_superuser):
    my_user = api_client_not_superuser.get("/user/me/").json()
    response = api_client_not_superuser.patch(
        f"/user/{my_user['id']}/password/",
        json={"password": "string", "password_confirm": "string1"},
    )
    assert response.status_code == 400
    result = response.json()
    assert result["detail"] == "Passwords don't match"


def test_change_password(api_client_not_superuser):
    my_user = api_client_not_superuser.get("/user/me/").json()
    response = api_client_not_superuser.patch(
        f"/user/{my_user['id']}/password/",
        json={"password": "string", "password_confirm": "string"},
    )
    assert response.status_code == 200
    result = response.json()
    assert result == my_user


def test_change_password_by_admin(api_client_authenticated):
    regular_user = api_client_authenticated.get("/user/regular/").json()
    response = api_client_authenticated.patch(
        f"/user/{regular_user['id']}/password/",
        json={"password": "string", "password_confirm": "string"},
    )
    assert response.status_code == 200
    result = response.json()
    assert result == regular_user


def test_delete_user_404(api_client_authenticated):
    response = api_client_authenticated.delete(
        "/user/99999/",
    )
    assert response.status_code == 404


def test_delete_user_self_not_allowed(api_client_authenticated):
    my_user = api_client_authenticated.get("/user/me/").json()
    response = api_client_authenticated.delete(
        f"/user/{my_user['id']}/",
    )
    assert response.status_code == 403


def test_delete_user(api_client_authenticated):
    user = api_client_authenticated.get("/user/foo/").json()
    response = api_client_authenticated.delete(
        f"/user/{user['id']}/",
    )
    assert response.status_code == 200
    result = response.json()
    assert result["ok"] == True
