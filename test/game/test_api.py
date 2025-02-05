import pytest
from django.test import Client


@pytest.fixture
def client() -> Client:
    return Client()


def test_hello_endpoint(client: Client) -> None:
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, welcome to AI Language Charades!"}
