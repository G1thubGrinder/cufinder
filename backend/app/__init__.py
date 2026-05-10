from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from .config import get_config
from .errors import register_error_handlers


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(get_config())

    CORS(
        app,
        resources={r"/api/*": {"origins": [app.config["FRONTEND_ORIGIN"]]}},
        supports_credentials=True,
    )

    register_error_handlers(app)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app
