import os
from flask import Flask
from .routes import bp
from .models import init_db

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("MYPLANNER_SECRET_KEY", "dev-secret-key")
    app.config["DB_PATH"] = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "events.db")
    os.makedirs(os.path.dirname(app.config["DB_PATH"]), exist_ok=True)

    init_db(app.config["DB_PATH"])
    app.register_blueprint(bp)

    return app
