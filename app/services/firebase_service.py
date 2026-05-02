"""Firebase Auth — verifies an ID token from the client and upserts the user."""
import os
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
from flask import current_app
from app.utils.api_error import ApiError
import app.database as _db
from . import user_service, token_service

_initialized = False


def _init():
    global _initialized
    if _initialized:
        return
    path = current_app.config.get("FIREBASE_CREDENTIALS_PATH", "")
    if not path or not os.path.exists(path):
        raise RuntimeError(
            "FIREBASE_CREDENTIALS_PATH is not set or the file is missing. "
            "Download your service account JSON from Firebase console."
        )
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.Certificate(path))
    _initialized = True


def verify_firebase_id_token(id_token: str) -> dict:
    _init()
    try:
        return firebase_auth.verify_id_token(id_token)
    except firebase_auth.ExpiredIdTokenError:
        raise ApiError.unauthorized("Firebase token has expired")
    except firebase_auth.InvalidIdTokenError:
        raise ApiError.unauthorized("Invalid Firebase token")
    except Exception as exc:
        current_app.logger.error("Firebase error: %s", exc)
        raise ApiError.unauthorized("Firebase authentication failed")


def login_or_create_with_firebase(id_token: str):
    claims = verify_firebase_id_token(id_token)

    firebase_uid = claims["uid"]
    email        = claims.get("email", "")
    name         = claims.get("name") or (email.split("@")[0] if email else "User")
    avatar       = claims.get("picture")

    user = user_service.get_user_by_social_id("firebase", firebase_uid)
    if not user and email:
        user = user_service.get_user_by_email(email)

    if user:
        updates: dict = {}
        if not user.firebase_uid:
            updates["firebase_uid"] = firebase_uid
        if avatar and not user.avatar:
            updates["avatar"] = avatar
        if updates:
            user = user_service.update_user(_db.record_id(user), updates)
    else:
        user = user_service.create_user({
            "name":             name,
            "email":            email,
            "firebase_uid":     firebase_uid,
            "avatar":           avatar,
            "is_email_verified": claims.get("email_verified", False),
        })

    tokens = token_service.generate_auth_tokens(_db.record_id(user))
    return user, tokens
