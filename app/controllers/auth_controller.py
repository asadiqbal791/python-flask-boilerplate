from flask import request
from flask_jwt_extended import get_jwt_identity
from http import HTTPStatus

from app.services import auth_service, user_service, token_service, email_service
from app.services import firebase_service, social_auth_service
from app.utils.api_response import success, created
from app.middlewares.auth import auth, get_current_user
from app.middlewares.validate import validate
from app.middlewares.rate_limiter import auth_limit, strict_limit
from app.validations import (
    RegisterSchema, LoginSchema, LogoutSchema, RefreshTokenSchema,
    ForgotPasswordSchema, ResetPasswordSchema, VerifyEmailSchema,
    FirebaseAuthSchema, SocialAuthSchema,
)


@auth_limit
@validate(RegisterSchema())
def register(validated: dict):
    """Register a new user."""
    user = user_service.create_user(validated)
    verify_token = token_service.generate_verify_email_token(
        str(user.id) if hasattr(user, "id") else user.id
    )
    email_service.send_verify_email(user.email, verify_token)
    tokens = token_service.generate_auth_tokens(
        str(user.id) if hasattr(user, "id") else user.id
    )
    return created({"user": user.to_dict(), "tokens": tokens}, "Registered successfully")


@auth_limit
@validate(LoginSchema())
def login(validated: dict):
    """Login with email and password."""
    user = auth_service.login_with_email_password(validated["email"], validated["password"])
    tokens = token_service.generate_auth_tokens(
        str(user.id) if hasattr(user, "id") else user.id
    )
    return success({"user": user.to_dict(), "tokens": tokens}, "Login successful")


@validate(LogoutSchema())
def logout(validated: dict):
    """Logout (blacklist refresh token)."""
    auth_service.logout(validated["refresh_token"])
    return success(message="Logged out")


@validate(RefreshTokenSchema())
def refresh_tokens(validated: dict):
    """Get new access/refresh token pair."""
    tokens = auth_service.refresh_auth(validated["refresh_token"])
    return success({"tokens": tokens})


@strict_limit
@validate(ForgotPasswordSchema())
def forgot_password(validated: dict):
    """Send reset-password email."""
    user = user_service.get_user_by_email(validated["email"])
    if user:
        token = token_service.generate_reset_password_token(
            str(user.id) if hasattr(user, "id") else user.id
        )
        email_service.send_reset_password_email(user.email, token)
    # Always return 200 to prevent email enumeration
    return success(message="If the email exists, a reset link has been sent")


@validate(ResetPasswordSchema())
def reset_password(validated: dict):
    """Reset password using token."""
    auth_service.reset_password(validated["token"], validated["password"])
    return success(message="Password reset successful")


def verify_email():
    """Verify email via token in query string."""
    token = request.args.get("token", "")
    if not token:
        from app.utils.api_error import ApiError
        raise ApiError.bad_request("Token is required")
    auth_service.verify_email(token)
    return success(message="Email verified")


@validate(FirebaseAuthSchema())
def firebase_login(validated: dict):
    """Login or register via Firebase ID token."""
    user, tokens = firebase_service.login_or_create_with_firebase(validated["id_token"])
    return success({"user": user.to_dict(), "tokens": tokens})


@validate(SocialAuthSchema())
def google_login(validated: dict):
    """Login or register via Google OAuth access token."""
    user, tokens = social_auth_service.login_with_google_token(validated["access_token"])
    return success({"user": user.to_dict(), "tokens": tokens})


@validate(SocialAuthSchema())
def github_login(validated: dict):
    """Login or register via GitHub OAuth access token."""
    user, tokens = social_auth_service.login_with_github_token(validated["access_token"])
    return success({"user": user.to_dict(), "tokens": tokens})


@validate(SocialAuthSchema())
def facebook_login(validated: dict):
    """Login or register via Facebook OAuth access token."""
    user, tokens = social_auth_service.login_with_facebook_token(validated["access_token"])
    return success({"user": user.to_dict(), "tokens": tokens})


@auth()
def get_me():
    """Get current authenticated user."""
    user = get_current_user()
    return success({"user": user.to_dict()})
