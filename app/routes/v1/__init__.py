from flask import Blueprint
from .auth_routes import auth_bp
from .user_routes import user_bp
from .oauth_routes import oauth_bp
from .config_routes import config_bp

v1_bp = Blueprint("v1", __name__, url_prefix="/v1")
v1_bp.register_blueprint(auth_bp)
v1_bp.register_blueprint(user_bp)
v1_bp.register_blueprint(oauth_bp)
v1_bp.register_blueprint(config_bp)
