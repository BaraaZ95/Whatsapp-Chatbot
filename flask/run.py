from factory import create_app
import os
import configparser

config = configparser.ConfigParser()

# Assuming .ini file is in the same directory as run.py
ini_file_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".ini"))

config.read(ini_file_path)

app = create_app()
app.config["DEBUG"] = True
app.config["MONGO_URI"] = config["PROD"]["DB_URI"]

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=os.environ.get(
            "FLASK_SERVER_PORT",
            5000),
        debug=True)  # type: ignore
