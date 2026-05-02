from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.utils.api_error import ApiError
from app.config.roles import ROLE_RIGHTS


def auth(*required_rights: str):
    """Decorator: verify JWT and optionally enforce RBAC rights.

    Usage:
        @auth()                         # just authenticated
        @auth("manageUsers")            # authenticated + has right
        @auth("deleteUsers", "manageSettings")  # all rights required
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception:
                raise ApiError.unauthorized()

            claims = get_jwt()
            if claims.get("type") not in ("access", None):
                raise ApiError.unauthorized("Invalid token type")

            if required_rights:
                user_id = get_jwt_identity()
                from app.services import user_service
                user = user_service.get_user_by_id(user_id)
                if not user:
                    raise ApiError.unauthorized()

                user_rights = ROLE_RIGHTS.get(user.role, [])
                user_param_id = kwargs.get("user_id")

                has_rights = all(r in user_rights for r in required_rights)
                is_own = user_param_id and str(user_param_id) == str(user_id)

                if not has_rights and not is_own:
                    raise ApiError.forbidden()

                from flask import g
                g.current_user = user

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def get_current_user():
    from flask import g
    from flask_jwt_extended import get_jwt_identity
    if hasattr(g, "current_user"):
        return g.current_user
    user_id = get_jwt_identity()
    from app.services import user_service
    return user_service.get_user_by_id(user_id)
