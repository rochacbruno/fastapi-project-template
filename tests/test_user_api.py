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

    # verify a username can't be used for multiple accounts
    response = api_client_authenticated.post(
        "/user/",
        json={
            "username": "foo",
            "password": "bar",
            "superuser": False,
            "disabled": False,
        },
    )
    assert response.status_code == 422


def test_user_by_id(api_client_authenticated):
    response = api_client_authenticated.get("/user/1")
    assert response.status_code == 200
    result = response.json()
    assert "admin" in result["username"]


def test_user_by_username(api_client_authenticated):
    response = api_client_authenticated.get("/user/admin")
    assert response.status_code == 200
    result = response.json()
    assert "admin" in result["username"]


def test_user_by_bad_id(api_client_authenticated):
    response = api_client_authenticated.get("/user/42")
    result = response.json()
    assert response.status_code == 404


def test_user_by_bad_username(api_client_authenticated):
    response = api_client_authenticated.get("/user/nouser")
    assert response.status_code == 404


def test_user_change_password_no_auth(api_client):

    # user doesn't exist
    response = api_client.patch(
        "/user/1/password/",
        json={"password": "foobar!", "password_confirm": "foobar!"},
    )
    assert response.status_code == 401


def test_user_change_password_insufficient_auth(api_client):

    # login as non-superuser
    token = api_client.post(
        "/token",
        data={"username": "foo", "password": "bar"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    ).json()["access_token"]
    api_client.headers["Authorization"] = f"Bearer {token}"

    # try to update admin user (id: 1)
    response = api_client.patch(
        "/user/1/password/",
        json={"password": "foobar!", "password_confirm": "foobar!"},
    )
    assert response.status_code == 403

    # log out
    del api_client.headers["Authorization"]


def test_user_change_password(api_client_authenticated):

    # user doesn't exist
    response = api_client_authenticated.patch(
        "/user/42/password/",
        json={"password": "foobar!", "password_confirm": "foobar!"},
    )
    assert response.status_code == 404

    foo_user = api_client_authenticated.get("/user/foo").json()
    assert "id" in foo_user

    # passwords don't match
    response = api_client_authenticated.patch(
        f"/user/{foo_user['id']}/password/",
        json={"password": "foobar!", "password_confirm": "foobar"},
    )
    assert response.status_code == 400

    # passwords do match
    response = api_client_authenticated.patch(
        f"/user/{foo_user['id']}/password/",
        json={"password": "foobar!", "password_confirm": "foobar!"},
    )
    assert response.status_code == 200


def test_user_delete_no_auth(api_client):

    # user doesn't exist
    response = api_client.delete("/user/42/")
    assert response.status_code == 401

    # valid delete request but not authorized
    response = api_client.delete(f"/user/1/")
    assert response.status_code == 401


def test_user_delete(api_client_authenticated):

    # user doesn't exist
    response = api_client_authenticated.delete("/user/42/")
    assert response.status_code == 404

    # try to delete yourself
    me = api_client_authenticated.get("/profile").json()
    assert "id" in me

    response = api_client_authenticated.delete(f"/user/{me['id']}/")
    assert response.status_code == 403

    # try to delete "foo" user
    foo_user = api_client_authenticated.get("/user/foo").json()
    assert "id" in foo_user

    # valid delete request
    response = api_client_authenticated.delete(f"/user/{foo_user['id']}/")
    assert response.status_code == 200


def test_bad_login(api_client):

    response = api_client.post(
        "/token",
        data={"username": "admin", "password": "admin1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401


def test_good_login(api_client):

    response = api_client.post(
        "/token",
        data={"username": "admin", "password": "admin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200


def test_refresh_token(api_client_authenticated):

    # create dummy account for test
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
    assert result["id"]
    user_id = result["id"]

    # retrieve access_token and refresh_token from newly created user
    response = api_client_authenticated.post(
        "/token",
        data={"username": "foo", "password": "bar"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["access_token"]
    assert result["refresh_token"]

    # use refresh_token to update access_token and refresh_token
    response = api_client_authenticated.post(
        "/refresh_token", json={"refresh_token": result["refresh_token"]}
    )

    assert response.status_code == 200
    result = response.json()
    assert result["access_token"]
    assert result["refresh_token"]

    # save refresh_token
    refresh_token = result["refresh_token"]

    # delete dummy account
    response = api_client_authenticated.delete(f"/user/{user_id}/")
    assert response.status_code == 200

    # confirm account was deleted
    response = api_client_authenticated.get(f"/user/{user_id}/")
    assert response.status_code == 404

    # try to refresh tokens
    response = api_client_authenticated.post(
        "/refresh_token", json={"refresh_token": refresh_token}
    )

    result = response.json()
    assert response.status_code == 401


def test_bad_refresh_token(api_client):

    BAD_TOKEN = "thisaintnovalidtoken"

    response = api_client.post(
        "/refresh_token", json={"refresh_token": BAD_TOKEN}
    )

    assert response.status_code == 401


# Need to add test for updating passwords with stale tokens
def test_stale_token(api_client_authenticated):

    # create non-admin account
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
    user_id = result["id"]

    # retrieve access_token and refresh_token from newly created user
    response = api_client_authenticated.post(
        "/token",
        data={"username": "foo", "password": "bar"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    result = response.json()

    # use refresh_token to update access_token and refresh_token
    response = api_client_authenticated.post(
        "/refresh_token", json={"refresh_token": result["refresh_token"]}
    )

    assert response.status_code == 200
    result = response.json()

    # set stale access_token
    api_client_authenticated.headers[
        "Authorization"
    ] = f"Bearer {result['access_token']}"

    response = api_client_authenticated.patch(
        f"/user/{user_id}/password/",
        json={"password": "foobar!", "password_confirm": "foobar!"},
    )
    assert response.status_code == 401

    del api_client_authenticated.headers["Authorization"]
