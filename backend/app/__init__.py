from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from .config import get_config
from .db import get_client
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

    # Lazy imports avoid circular import issues at module load time.
    from .auth.routes import auth_bp
    from .items.routes import items_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(items_bp)

    @app.get("/api/health")
    def health():
        get_client().admin.command("ping")
        return jsonify({"status": "ok"})

    return app
