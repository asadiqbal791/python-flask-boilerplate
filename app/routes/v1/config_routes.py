"""Public config endpoint — exposes only non-secret client IDs for the frontend."""
from flask import Blueprint, jsonify, current_app

config_bp = Blueprint("config", __name__, url_prefix="/config")


@config_bp.get("/public")
def public_config():
    """Return public OAuth client IDs safe to expose to the browser."""
    app = current_app
    return jsonify({
        "googleClientId":  app.config.get("GOOGLE_CLIENT_ID", ""),
        "githubClientId":  app.config.get("GITHUB_CLIENT_ID", ""),
        "facebookAppId":   app.config.get("FACEBOOK_CLIENT_ID", ""),
    })
