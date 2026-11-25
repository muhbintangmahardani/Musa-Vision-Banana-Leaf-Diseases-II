"""Flask HTTP Blueprints separating web page routes from JSON prediction APIs."""

from musavision.routes.api_routes import api_bp
from musavision.routes.web_routes import web_bp

__all__ = ["api_bp", "web_bp"]
