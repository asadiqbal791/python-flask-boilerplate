from http import HTTPStatus
from app.utils.api_error import ApiError
import app.database as _db


def create_user(data: dict):
    User = _db.get_user_model()

    if get_user_by_email(data["email"]):
        raise ApiError(HTTPStatus.CONFLICT, "Email already taken")

    user = User(
        name=data["name"],
        email=data["email"].lower(),
        role=data.get("role", "user"),
    )

    # Optional fields
    for field in ("google_id", "github_id", "facebook_id", "firebase_uid", "avatar"):
        if data.get(field):
            setattr(user, field, data[field])

    if data.get("is_email_verified"):
        user.is_email_verified = data["is_email_verified"]

    if data.get("password"):
        user.set_password(data["password"])

    _db.save(user)
    return user


def get_user_by_id(user_id: str):
    return _db.get_by_id(_db.get_user_model(), user_id)


def get_user_by_email(email: str):
    return _db.find_one(_db.get_user_model(), email=email.lower())


def get_user_by_social_id(provider: str, provider_id: str):
    User = _db.get_user_model()
    field = f"{provider}_id"
    return _db.find_one(User, **{field: provider_id})


def update_user(user_id: str, update_data: dict):
    user = get_user_by_id(user_id)
    if not user:
        raise ApiError.not_found("User not found")

    if "email" in update_data:
        existing = get_user_by_email(update_data["email"])
        if existing and _db.record_id(existing) != str(user_id):
            raise ApiError(HTTPStatus.CONFLICT, "Email already taken")
        update_data["email"] = update_data["email"].lower()

    for key, val in update_data.items():
        if key == "password":
            user.set_password(val)
        else:
            setattr(user, key, val)

    _db.save(user)
    return user


def delete_user(user_id: str):
    user = get_user_by_id(user_id)
    if not user:
        raise ApiError.not_found("User not found")
    _db.delete(user)


def query_users(filters: dict, page: int, limit: int):
    User = _db.get_user_model()

    from flask import current_app
    if current_app.config.get("MONGO_ENABLED"):
        q = User.objects
        if filters.get("name"):
            q = q.filter(name__icontains=filters["name"])
        if filters.get("role"):
            q = q.filter(role=filters["role"])
        total = q.count()
        items = list(q.skip((page - 1) * limit).limit(limit))
        return items, total
    else:
        from app.utils.pagination import paginate_query
        q = User.query
        if filters.get("name"):
            q = q.filter(User.name.ilike(f"%{filters['name']}%"))
        if filters.get("role"):
            q = q.filter_by(role=filters["role"])
        return paginate_query(q, page, limit)
