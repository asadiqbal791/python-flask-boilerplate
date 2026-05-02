"""Request validation decorator using Marshmallow schemas."""
from functools import wraps
from flask import request
from marshmallow import Schema, ValidationError
from app.utils.api_error import ApiError


def validate(schema: Schema, source: str = "json"):
    """Validate request data against a Marshmallow schema.

    source: 'json' | 'args' | 'form'
    Parsed data is injected as the first positional argument 'validated'.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if source == "json":
                raw = request.get_json(silent=True) or {}
            elif source == "args":
                raw = request.args.to_dict()
            elif source == "form":
                raw = request.form.to_dict()
            else:
                raw = {}

            try:
                data = schema.load(raw)
            except ValidationError as err:
                raise ApiError(400, "Validation error: " + str(err.messages))

            kwargs["validated"] = data
            return fn(*args, **kwargs)
        return wrapper
    return decorator
