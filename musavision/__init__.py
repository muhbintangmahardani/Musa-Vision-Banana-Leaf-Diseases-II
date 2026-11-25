"""MusaVision Flask Application Factory."""

from flask import Flask

from musavision.config import MAX_CONTENT_LENGTH, STATIC_DIR, TEMPLATE_DIR
from musavision.routes import api_bp, web_bp
from musavision.services.yolo_detector import get_model


def create_app() -> Flask:
    """Create and configure the Flask application instance and warm up YOLO weights."""
    application = Flask(
        __name__,
        template_folder=str(TEMPLATE_DIR),
        static_folder=str(STATIC_DIR),
    )
    application.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    get_model()

    application.register_blueprint(web_bp)
    application.register_blueprint(api_bp)
    return application
