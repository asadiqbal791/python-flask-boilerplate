from marshmallow import Schema, fields, validate, validates, ValidationError


class RegisterSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=128))
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=8, max=128),
            validate.Regexp(
                r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)",
                error="Password must contain at least one uppercase letter, one lowercase letter and one digit",
            ),
        ],
        load_only=True,
    )


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class RefreshTokenSchema(Schema):
    refresh_token = fields.Str(required=True, data_key="refreshToken")


class LogoutSchema(Schema):
    refresh_token = fields.Str(required=True, data_key="refreshToken")


class ForgotPasswordSchema(Schema):
    email = fields.Email(required=True)


class ResetPasswordSchema(Schema):
    token = fields.Str(required=True)
    password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=8, max=128),
            validate.Regexp(
                r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)",
                error="Password must contain uppercase, lowercase and a digit",
            ),
        ],
        load_only=True,
    )


class VerifyEmailSchema(Schema):
    token = fields.Str(required=True)


class FirebaseAuthSchema(Schema):
    id_token = fields.Str(required=True, data_key="idToken")


class SocialAuthSchema(Schema):
    access_token = fields.Str(required=True, data_key="accessToken")
