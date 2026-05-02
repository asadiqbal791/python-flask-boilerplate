from http import HTTPStatus
from app.utils.api_error import ApiError
import app.database as _db
from app.config.tokens import TokenType
from . import user_service, token_service


def login_with_email_password(email: str, password: str):
    user = user_service.get_user_by_email(email)
    if not user or not user.check_password(password):
        raise ApiError(HTTPStatus.UNAUTHORIZED, "Incorrect email or password")
    if not user.is_active:
        raise ApiError(HTTPStatus.UNAUTHORIZED, "Account is deactivated")
    return user


def logout(refresh_token: str) -> None:
    record = token_service.verify_token(refresh_token, TokenType.REFRESH)
    token_service.blacklist_token(record)


def refresh_auth(refresh_token: str) -> dict:
    record = token_service.verify_token(refresh_token, TokenType.REFRESH)
    user_id = _db.record_id(record.user) if hasattr(record, "user") and record.user else record.user_id
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise ApiError.unauthorized()
    token_service.blacklist_token(record)
    return token_service.generate_auth_tokens(_db.record_id(user))


def reset_password(reset_token: str, new_password: str) -> None:
    try:
        record = token_service.verify_token(reset_token, TokenType.RESET_PASSWORD)
    except ApiError:
        raise ApiError(HTTPStatus.UNAUTHORIZED, "Password reset failed")

    user_id = _resolve_user_id(record)
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise ApiError(HTTPStatus.UNAUTHORIZED, "Password reset failed")

    user_service.update_user(user_id, {"password": new_password})
    token_service.delete_tokens_by_user(user_id, TokenType.RESET_PASSWORD)


def verify_email(verify_token: str) -> None:
    try:
        record = token_service.verify_token(verify_token, TokenType.VERIFY_EMAIL)
    except ApiError:
        raise ApiError(HTTPStatus.UNAUTHORIZED, "Email verification failed")

    user_id = _resolve_user_id(record)
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise ApiError(HTTPStatus.UNAUTHORIZED, "Email verification failed")

    token_service.delete_tokens_by_user(user_id, TokenType.VERIFY_EMAIL)
    user_service.update_user(user_id, {"is_email_verified": True})


def _resolve_user_id(token_record) -> str:
    """Extract user ID string from a token record regardless of engine."""
    if hasattr(token_record, "user") and token_record.user:
        return _db.record_id(token_record.user)
    return token_record.user_id
