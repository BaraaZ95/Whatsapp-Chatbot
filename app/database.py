from datetime import datetime
from typing import List
from flask import current_app, g
from werkzeug.local import LocalProxy
from flask_pymongo import PyMongo
from mongomock import MongoClient
from typing import Optional


def get_db():
    """
    Configuration method to return db instance
    """
    db = getattr(g, "_database", None)

    if db is None:
        db = g._database = PyMongo(current_app).db

    return db


# Use LocalProxy to read the global db instance with just `db`
db = LocalProxy(get_db)


def check_user_exists(
    phone_number: str,
) -> bool:
    """
    Check if a user with the given phone number exists in the database.

    Parameters:
        phone_number (str): The phone number of the user.

    Returns:
        bool: True if a user with the given phone number exists, False otherwise.
    """
    users_db = db["Users"]  # type: ignore
    user_details = users_db.find_one({"phone_number": phone_number})
    if user_details is None:
        return False
    else:
        return True


def add_user(
    phone_number: str,
) -> None:  # If a referral who's number isn't on the db contacted the bot
    """
    Adds a user to the database.

    :param phone_number: The phone number of the user.
    :type phone_number: str
    :return: None
    """
    users_db = db["Users"]  # type: ignore
    response = users_db.insert_one({"phone_number": phone_number})
    print("user with phone number " + phone_number + " doesn't exist. Added to db")
    return response


def save_message(
    message_text: str,
    phone_number: str,
    AI_response: bool = False,
    db_connection: Optional[MongoClient] = None,
) -> None:
    """
    Saves a message to the Messages database.

    :param message_text: The text of the message to be saved. (str)
    :param phone_number: The phone number associated with the message. (str)
    :param AI_response: Whether the message is a response generated by AI. (bool)
    :param db_connection: MongoDB connection object. (Optional[MongoClient])
    :return: The response object returned by the database insert operation. (None)
    """
    if db_connection is None:
        from flask import g

        # Used to create an in-memory fake db for testing
        db_connection = getattr(g, "_database", None)
        if db_connection is None:
            raise RuntimeError("No MongoDB connection found.")

    messages_db = db_connection["Messages"]
    message_dict = {
        "phone_number": phone_number,
        "timestamp": datetime.now(),
        "message_text": message_text,
        "AI_response": AI_response,
    }
    response = messages_db.insert_one(message_dict)
    return response


def get_message_history(phone_number) -> List:
    """
    Retrieves the message history for a given phone number.

    Args:
        phone_number (str): The phone number for which to retrieve the message history.

    Returns:
        List[Dict[str, str]]: A list of dictionaries representing the cleaned messages. Each dictionary contains either an "input" or an "output" key, depending on whether the message was an AI response or user input.
    """
    # users_db = db["Users"]
    messages_db = db["Messages"]  # type: ignore
    cleaned_messages = []
    # user_details = users_db.find_one({"phone_number":phone_number},  {"username": 1, "user_id": 0, "_id":0})
    # username = user_details["username"] # Can user username instead of Human
    # tag in the responses
    messages = messages_db.find(
        {"phone_number": phone_number},
        {"message_text": 1, "AI_response": 1, "_id": 0},
    ).sort("timestamp", -1)
    messages_list = [msg for msg in messages]

    for message in messages_list:
        if message["AI_response"] is True:
            cleaned_dict = {
                "output": message["message_text"],
            }
        else:
            cleaned_dict = {
                "input": message["message_text"],
            }
        cleaned_messages.append(cleaned_dict)
    return cleaned_messages