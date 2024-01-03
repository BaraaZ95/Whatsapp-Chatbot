import sys
import pytest

sys.path.insert(0, "/home/baraa/Projects/realestate/ChatGPT_Whatsapp_Bot/")
from factory import create_app  # noqa: E402


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app(testing=False)
    app.config["TESTING"] = True
    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


def test_your_function(client):
    # Your test code here
    response = client.get("/", follow_redirects=True)

    assert response.status_code == 200


def test_index_html_contains_hello_world(client):
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200
    assert b"Hello, World!" in response.data
