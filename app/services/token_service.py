from datetime import datetime, timezone, timedelta
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

import app.database as _db
from app.config.tokens import TokenType
from app.utils.api_error import ApiError


def generate_auth_tokens(user_id: str) -> dict:
    cfg = current_app.config
    access_expires  = cfg.get("JWT_ACCESS_TOKEN_EXPIRES",  timedelta(minutes=30))
    refresh_expires = cfg.get("JWT_REFRESH_TOKEN_EXPIRES", timedelta(days=30))

    access_token = create_access_token(
        identity=user_id,
        expires_delta=access_expires,
        additional_claims={"type": TokenType.ACCESS},
    )
    refresh_token = create_refresh_token(
        identity=user_id,
        expires_delta=refresh_expires,
    )

    _save_token(refresh_token, user_id, TokenType.REFRESH,
                datetime.now(timezone.utc) + refresh_expires)

    return {
        "access": {
            "token": access_token,
            "expires": (datetime.now(timezone.utc) + access_expires).isoformat(),
        },
        "refresh": {
            "token": refresh_token,
            "expires": (datetime.now(timezone.utc) + refresh_expires).isoformat(),
        },
    }


def generate_reset_password_token(user_id: str) -> str:
    minutes = current_app.config.get("JWT_RESET_PASSWORD_EXPIRATION_MINUTES", 10)
    return _generate_one_time_token(user_id, TokenType.RESET_PASSWORD, timedelta(minutes=minutes))


def generate_verify_email_token(user_id: str) -> str:
    minutes = current_app.config.get("JWT_VERIFY_EMAIL_EXPIRATION_MINUTES", 10)
    return _generate_one_time_token(user_id, TokenType.VERIFY_EMAIL, timedelta(minutes=minutes))


def verify_token(token: str, expected_type: str):
    """Decode token, validate type, and return the DB record."""
    try:
        payload = decode_token(token)
    except ExpiredSignatureError:
        raise ApiError.unauthorized("Token has expired")
    except Exception:
        raise ApiError.unauthorized("Invalid token")

    if payload.get("type") != expected_type:
        raise ApiError.unauthorized("Invalid token type")

    record = _db.find_one(_db.get_token_model(), token=token, type=expected_type, blacklisted=False)
    if not record:
        raise ApiError.unauthorized("Token not found or already used")
    return record


def blacklist_token(token_record) -> None:
    token_record.blacklisted = True
    _db.save(token_record)


def delete_tokens_by_user(user_id: str, token_type: str) -> None:
    Token = _db.get_token_model()
    from flask import current_app
    if current_app.config.get("MONGO_ENABLED"):
        Token.objects(user=user_id, type=token_type).delete()
    else:
        from app.extensions import db
        Token.query.filter_by(user_id=user_id, type=token_type).delete()
        db.session.commit()


def _generate_one_time_token(user_id: str, token_type: str, expires: timedelta) -> str:
    token = create_access_token(
        identity=user_id,
        expires_delta=expires,
        additional_claims={"type": token_type},
    )
    _save_token(token, user_id, token_type, datetime.now(timezone.utc) + expires)
    return token


def _save_token(token: str, user_id: str, token_type: str, expires: datetime) -> None:
    Token = _db.get_token_model()
    from flask import current_app
    if current_app.config.get("MONGO_ENABLED"):
        record = Token(token=token, user=user_id, type=token_type, expires=expires)
    else:
        record = Token(token=token, user_id=user_id, type=token_type, expires=expires)
    _db.save(record)
