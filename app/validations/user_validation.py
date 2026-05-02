from marshmallow import Schema, fields, validate
from app.config.roles import ALL_ROLES


class CreateUserSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=128))
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8),
        load_only=True,
    )
    role = fields.Str(validate=validate.OneOf(ALL_ROLES), load_default="user")


class UpdateUserSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=128))
    email = fields.Email()
    password = fields.Str(validate=validate.Length(min=8), load_only=True)
    role = fields.Str(validate=validate.OneOf(ALL_ROLES))


class UserQuerySchema(Schema):
    name = fields.Str(load_default=None)
    role = fields.Str(validate=validate.OneOf(ALL_ROLES), load_default=None)
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    limit = fields.Int(load_default=10, validate=validate.Range(min=1, max=100))
    sort_by = fields.Str(load_default="created_at", data_key="sortBy")
    sort_order = fields.Str(
        load_default="desc",
        validate=validate.OneOf(["asc", "desc"]),
        data_key="sortOrder",
    )
