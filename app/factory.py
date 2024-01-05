import os
from flask import Flask, render_template
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from bson import json_util, ObjectId
from datetime import datetime
import logging
from flask_talisman import Talisman
from flask_sslify import SSLify


from BOT_API import chatbot_api_v1


def get_config_value(config_path, section, key):
    import configparser

    config = configparser.ConfigParser()
    config.read(config_path)
    return config[section][key]


class MongoJsonEncoder(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, ObjectId):
            return str(obj)
        return json_util.default(obj, json_util.CANONICAL_JSON_OPTIONS)


def create_app(testing=False):
    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    STATIC_FOLDER = os.path.join(APP_DIR, "build/static")
    TEMPLATE_FOLDER = os.path.join(APP_DIR, "templates")

    app = Flask(
        __name__,
        static_folder=STATIC_FOLDER,
        template_folder=TEMPLATE_FOLDER,
    )

    app.json_provider_class = MongoJsonEncoder
    app.json = MongoJsonEncoder(app)
    app.register_blueprint(chatbot_api_v1)

    config_path = os.path.join(APP_DIR, ".ini")
    if testing:
        # Load the appropriate configuration from the INI file for testing
        config_section = "TEST"
    config_section = "TEST" if testing else "PROD"
    app.config["MONGO_URI"] = get_config_value(config_path, config_section, "DB_URI")

    if app.config["TESTING"] is False:
        CORS(app)
        Talisman(app)
        SSLify(app)
        app.config["PROPAGATE_EXCEPTIONS"] = True
        app.logger.setLevel(logging.INFO)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve(path):
        return render_template("index.html")

    return app
