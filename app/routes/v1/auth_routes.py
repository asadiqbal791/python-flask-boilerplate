from flask import Blueprint
from app.controllers import auth_controller as ctrl

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Custom JWT auth
auth_bp.post("/register")(ctrl.register)
auth_bp.post("/login")(ctrl.login)
auth_bp.post("/logout")(ctrl.logout)
auth_bp.post("/refresh-tokens")(ctrl.refresh_tokens)
auth_bp.post("/forgot-password")(ctrl.forgot_password)
auth_bp.post("/reset-password")(ctrl.reset_password)
auth_bp.get("/verify-email")(ctrl.verify_email)
auth_bp.get("/me")(ctrl.get_me)

# Firebase Auth
auth_bp.post("/firebase")(ctrl.firebase_login)

# Social Auth
auth_bp.post("/google")(ctrl.google_login)
auth_bp.post("/github")(ctrl.github_login)
auth_bp.post("/facebook")(ctrl.facebook_login)
