def test_using_testing_db(settings):
    assert settings.db.uri == "sqlite:///testing.db"


def test_index(api_client):
    response = api_client.get("/")
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "Hello World!"


def test_cors_header(api_client):
    valid_origin = ["http://localhost:3000", "http://localhost:4200"]
    invalid_origin = ["http://localhost:3200", "http://localhost:4000"]

    valid_responses = [
        api_client.options(
            "/",
            headers={
                "Origin": f"{url}",
            },
        )
        for url in valid_origin
    ]

    for res, url in zip(valid_responses, valid_origin):
        assert res.headers.get("access-control-allow-origin") == url

    invalid_responses = [
        api_client.options(
            "/",
            headers={
                "Origin": f"{url}",
            },
        )
        for url in invalid_origin
    ]

    for res in invalid_responses:
        assert res.headers.get("access-control-allow-origin") is None
