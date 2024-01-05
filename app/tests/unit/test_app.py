import sys
import pytest
import os

current_dir = os.getcwd()
flask_path = os.path.join(current_dir, "app")
print("Path: ", flask_path)
sys.path.insert(0, flask_path)
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
    assert b"Baraa" in response.data
