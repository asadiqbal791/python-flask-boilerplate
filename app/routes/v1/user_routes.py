from flask import Blueprint
from app.controllers import user_controller as ctrl

user_bp = Blueprint("users", __name__, url_prefix="/users")

# Admin endpoints
user_bp.post("/")(ctrl.create_user)
user_bp.get("/")(ctrl.get_users)
user_bp.get("/<string:user_id>")(ctrl.get_user)
user_bp.patch("/<string:user_id>")(ctrl.update_user)
user_bp.delete("/<string:user_id>")(ctrl.delete_user)

# Self-service
user_bp.get("/me")(ctrl.get_profile)
user_bp.patch("/me")(ctrl.update_profile)
