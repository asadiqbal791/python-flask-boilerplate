from flask import Blueprint
from .auth_routes import auth_bp
from .user_routes import user_bp

v1_bp = Blueprint("v1", __name__, url_prefix="/v1")
v1_bp.register_blueprint(auth_bp)
v1_bp.register_blueprint(user_bp)
