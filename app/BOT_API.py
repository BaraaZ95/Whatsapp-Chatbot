from flask import Blueprint, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from database import (
    add_user,
    check_user_exists,
    save_message,
)
from llm import LanguageModelHandler
import requests

# from utils import expect
from pymongo.errors import DuplicateKeyError


load_dotenv()

TWILIO_ACCOUNT_SID = str(os.getenv("TWILIO_ACCOUNT_SID"))
TWILIO_AUTH_TOKEN = str(os.getenv("TWILIO_AUTH_TOKEN"))

chatbot_api_v1 = Blueprint(
    "chatbot_api_v1", "chatbot_api_v1", url_prefix="/api/v1/chatbot"
)
CORS(chatbot_api_v1)


def generate_answer(phone_number, message_received):
    conversation = LanguageModelHandler(phone_number=phone_number)
    query_result = conversation.get_response(user_input=message_received)
    query_result = str(query_result)
    save_message(phone_number=phone_number, message_text=query_result, AI_response=True)
    return query_result


@chatbot_api_v1.errorhandler(DuplicateKeyError)
def resource_not_found(e):
    """
    An error-handler to ensure that MongoDB duplicate key errors are returned as JSON.
    """
    return jsonify(error=f"Duplicate key error: {e}"), 400


@chatbot_api_v1.route("/send_first_message", methods=["POST"])
def send_first_message():
    try:
        phone_number = request.form.get("phone_number")
        message_body = request.form.get("message_body")

        url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
        data = {
            "To": f"whatsapp:{phone_number}",
            "From": "whatsapp:+14155238886",
            "Body": str(message_body),
        }
        auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        response = requests.post(url, data=data, auth=auth)

        return response.text, 201
    except Exception as e:
        return f"Twilio API error: {e}", 500


# Define a route to handle incoming requests
@chatbot_api_v1.route("/chat", methods=["POST"])
def chat():
    phone_number = request.form["From"].replace("whatsapp:", "").strip()
    message_received = request.form["Body"].strip()

    if check_user_exists(phone_number=phone_number):
        print("Agent number already exists")
    else:
        print("Agent number doesn't exist. Adding agent details to db")
        add_user(phone_number=phone_number)

    save_message(phone_number=phone_number, message_text=message_received)

    answer = generate_answer(phone_number, message_received)

    return jsonify({"BOT Answer: ", answer}), 201
