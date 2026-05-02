"""Database abstraction layer.

All services import from here instead of checking MONGO_ENABLED themselves.
Switching engines is a single env-var change — no code changes needed.

Usage in services:
    from app.database import get_user_model, get_token_model, commit, save, delete
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.sql.user import User
    from app.models.sql.token import Token
    from app.models.mongo.user import MongoUser
    from app.models.mongo.token import MongoToken


def _is_mongo() -> bool:
    from flask import current_app
    return bool(current_app.config.get("MONGO_ENABLED"))


def get_user_model():
    """Return the active User model class."""
    if _is_mongo():
        from app.models.mongo.user import MongoUser
        return MongoUser
    from app.models.sql.user import User
    return User


def get_token_model():
    """Return the active Token model class."""
    if _is_mongo():
        from app.models.mongo.token import MongoToken
        return MongoToken
    from app.models.sql.token import Token
    return Token


def commit():
    """Flush + commit for SQL; no-op for Mongo (saves are explicit)."""
    if not _is_mongo():
        from app.extensions import db
        db.session.commit()


def save(obj) -> None:
    """Persist a model instance for whichever engine is active."""
    if _is_mongo():
        obj.save()
    else:
        from app.extensions import db
        db.session.add(obj)
        db.session.commit()


def delete(obj) -> None:
    """Delete a model instance."""
    if _is_mongo():
        obj.delete()
    else:
        from app.extensions import db
        db.session.delete(obj)
        db.session.commit()


def bulk_delete_query(model_cls, **filters) -> None:
    """Delete all records matching filters."""
    if _is_mongo():
        model_cls.objects(**filters).delete()
    else:
        from app.extensions import db
        model_cls.query.filter_by(**filters).delete()
        db.session.commit()


def find_one(model_cls, **filters):
    """Return first matching record or None."""
    if _is_mongo():
        mongo_filters = {k: v for k, v in filters.items()}
        return model_cls.objects(**mongo_filters).first()
    return model_cls.query.filter_by(**filters).first()


def get_by_id(model_cls, record_id: str):
    """Return a record by primary key or None."""
    if _is_mongo():
        return model_cls.objects(id=record_id).first()
    return model_cls.query.get(record_id)


def record_id(obj) -> str:
    """Return the string ID of a model instance regardless of engine."""
    if _is_mongo():
        return str(obj.id)
    return obj.id
