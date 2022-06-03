def test_content_create(api_client_authenticated):
    response = api_client_authenticated.post(
        "/content/",
        json={
            "title": "hello test",
            "text": "this is just a test",
            "published": True,
            "tags": ["test", "hello"],
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert result["slug"] == "hello-test"


def test_content_list(api_client_authenticated):
    response = api_client_authenticated.get("/content/")
    assert response.status_code == 200
    result = response.json()
    assert result[0]["slug"] == "hello-test"


def test_content_get_individual(api_client_authenticated):
    response = api_client_authenticated.get("/content/hello-test")
    assert response.status_code == 200
    result = response.json()
    assert result["slug"] == "hello-test"


def test_content_get_individual_404(api_client_authenticated):
    response = api_client_authenticated.get("/content/does-not-exist/")
    assert response.status_code == 404


def test_content_update(api_client_authenticated):
    response = api_client_authenticated.post(
        "/content/",
        json={
            "title": "Test Post 2 for Patch",
            "text": "this is just a test",
            "published": True,
            "tags": ["test", "hello"],
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert result["slug"] == "test-post-2-for-patch"
    response2 = api_client_authenticated.patch(
        f"/content/{result['id']}/",
        json={
            "published": "false",
        },
    )
    assert response2.status_code == 200
    result2 = response2.json()
    assert result["slug"] == result2["slug"]
    assert result["text"] == result2["text"]
    assert result["tags"] == result2["tags"]
    assert result["published"] != result2["published"]


def test_content_update_404(api_client_authenticated):
    response = api_client_authenticated.patch(
        "/content/999/",
        json={
            "published": "false",
        },
    )
    assert response.status_code == 404


def test_content_update_unauthorized(api_client_not_superuser):
    response = api_client_not_superuser.patch(
        "/content/1/",
        json={
            "published": "false",
        },
    )
    assert response.status_code == 403
