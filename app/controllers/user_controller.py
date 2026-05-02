from flask_jwt_extended import get_jwt_identity
from http import HTTPStatus

from app.services import user_service
from app.utils.api_response import success, created, no_content, paginated
from app.middlewares.auth import auth
from app.middlewares.validate import validate
from app.validations import CreateUserSchema, UpdateUserSchema, UserQuerySchema
from app.utils.pagination import get_pagination_params


@auth("manageUsers")
@validate(CreateUserSchema())
def create_user(validated: dict):
    """Admin: create a new user."""
    user = user_service.create_user(validated)
    return created({"user": user.to_dict()}, "User created")


@auth("getUsers")
@validate(UserQuerySchema(), source="args")
def get_users(validated: dict):
    """Admin: list users with pagination and filtering."""
    page = validated.pop("page", 1)
    limit = validated.pop("limit", 10)
    validated.pop("sort_by", None)
    validated.pop("sort_order", None)
    filters = {k: v for k, v in validated.items() if v is not None}
    items, total = user_service.query_users(filters, page, limit)
    return paginated([u.to_dict() for u in items], total, page, limit)


@auth("getUsers")
def get_user(user_id: str):
    """Get user by ID."""
    user = user_service.get_user_by_id(user_id)
    if not user:
        from app.utils.api_error import ApiError
        raise ApiError.not_found("User not found")
    return success({"user": user.to_dict()})


@auth("manageUsers")
@validate(UpdateUserSchema())
def update_user(user_id: str, validated: dict):
    """Update a user."""
    user = user_service.update_user(user_id, validated)
    return success({"user": user.to_dict()}, "User updated")


@auth("deleteUsers")
def delete_user(user_id: str):
    """Delete a user."""
    user_service.delete_user(user_id)
    return no_content()


@auth()
def get_profile():
    """Get the currently authenticated user's profile."""
    user_id = get_jwt_identity()
    user = user_service.get_user_by_id(user_id)
    if not user:
        from app.utils.api_error import ApiError
        raise ApiError.not_found("User not found")
    return success({"user": user.to_dict()})


@auth()
@validate(UpdateUserSchema())
def update_profile(validated: dict):
    """Update the currently authenticated user's profile."""
    user_id = get_jwt_identity()
    # Prevent self-role escalation
    validated.pop("role", None)
    user = user_service.update_user(user_id, validated)
    return success({"user": user.to_dict()}, "Profile updated")
