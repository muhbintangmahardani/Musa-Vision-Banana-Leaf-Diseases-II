"""Web page routes rendering Jinja2 templates with unified navigation context."""

from flask import Blueprint, render_template

from musavision.services.yolo_detector import get_loaded_model_path, is_model_loaded

web_bp = Blueprint("web", __name__)


@web_bp.route("/", methods=["GET"])
def index():
    """Render the main landing page."""
    return render_template(
        "index.html",
        active_page="landing",
        model_loaded=is_model_loaded(),
        model_path=get_loaded_model_path(),
    )


@web_bp.route("/deteksi", methods=["GET"])
def deteksi():
    """Render the standalone AI leaf detection workspace."""
    return render_template("deteksi.html", active_page="deteksi")


@web_bp.route("/katalog-patogen", methods=["GET"])
def katalog_patogen():
    """Render the five-class banana leaf pathology catalog."""
    return render_template("katalog_patogen.html", active_page="katalog")
