import sys
from mongomock import MongoClient
import pytest
from datetime import datetime
from flask import g
from flask_pymongo import PyMongo
import os

current_dir = os.getcwd()
flask_path = os.path.join(current_dir, "app")
print("Path: ", flask_path)
sys.path.insert(0, flask_path)

from factory import create_app  # noqa: E402
from database import save_message, get_message_history  # noqa: E402


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


@pytest.fixture
def mock_db():
    return MongoClient().db


@pytest.fixture
def mongo(request, app):
    """
    Create a mock MongoDB and clean it up after the test.

    :param request: Pytest fixture for request details.
    :param app: Flask app instance.
    :return: mongomock.MongoClient
    """
    client = MongoClient()
    app.config[
        "MONGO_URI"
    ] = client  # Override the real MongoDB URI with the mock client

    def teardown():
        client.close()

    request.addfinalizer(teardown)
    return client


def test_mongodb_connection(app):
    with app.app_context():
        mongo = PyMongo(app)

        if mongo.db is None:
            pytest.fail("MongoDB connection is not properly set up")

        try:
            mongo.db.command("ping")
        except Exception as e:
            pytest.fail(f"Failed to connect to MongoDB: {str(e)}")


def test_fake_user_creation(app, mock_db):
    with app.app_context():
        users_db = mock_db["Users"]

        fake_user = {
            "phone_number": "1234567890",
            # Add other fields as needed
        }

        users_db.insert_one(fake_user)

        inserted_user = users_db.find_one({"phone_number": "1234567890"})
        assert inserted_user is not None
        assert inserted_user["phone_number"] == fake_user["phone_number"]


def test_save_message(app, mock_db):
    message_text = "Hello, this is a test message."
    phone_number = "1234567890"
    ai_response = False

    with app.app_context():
        g._database = mock_db
        save_message(message_text, phone_number, ai_response)

    messages_db = mock_db["Messages"]
    saved_message = messages_db.find_one({"phone_number": phone_number})

    assert saved_message is not None
    assert saved_message["message_text"] == message_text
    assert saved_message["AI_response"] == ai_response
    assert saved_message["phone_number"] == phone_number
    assert "timestamp" in saved_message
    assert isinstance(saved_message["timestamp"], datetime)


def test_get_message_history(app, mock_db):
    phone_number = "1234567890"

    with app.app_context():
        g._database = mock_db
        result = get_message_history(phone_number)

    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)
    assert all("input" in item or "output" in item for item in result)
