def test_using_testing_db(settings):
    assert settings.db.uri == "sqlite:///testing.db"


def test_index(api_client):
    response = api_client.get("/")
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "Hello World!"
