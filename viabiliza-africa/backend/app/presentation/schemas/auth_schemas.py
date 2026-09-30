from marshmallow import Schema, fields, validate

from app.domain.enums.user_role import UserRole


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=1))


class RegisterUserSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
    full_name = fields.String(required=True, validate=validate.Length(min=2, max=200))
    role = fields.String(
        required=True,
        validate=validate.OneOf(
            [UserRole.FINANCIAL.value, UserRole.USER.value, UserRole.BANK.value]
        ),
    )
    bank_code = fields.String(required=False, allow_none=True)


class PasswordRecoverySchema(Schema):
    email = fields.Email(required=True)


class ResetPasswordSchema(Schema):
    token = fields.String(required=True, validate=validate.Length(min=10))
    new_password = fields.String(required=True, validate=validate.Length(min=8))


class RefreshTokenSchema(Schema):
    refresh_token = fields.String(required=True)


class LogoutSchema(Schema):
    refresh_token = fields.String(required=False, load_default=None)


class SignupOtpRequestSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
    full_name = fields.String(required=True, validate=validate.Length(min=2, max=200))
    terms_accepted = fields.Boolean(required=True)
    terms_version = fields.String(required=False, load_default=None)


class SignupOtpVerifySchema(Schema):
    email = fields.Email(required=True)
    code = fields.String(required=True, validate=validate.Length(equal=6))
    terms_accepted = fields.Boolean(required=True)
    terms_version = fields.String(required=False, load_default=None)


class SignupOtpResendSchema(Schema):
    email = fields.Email(required=True)


class GoogleAuthSchema(Schema):
    credential = fields.String(required=False, load_default=None)
    code = fields.String(required=False, load_default=None)
    terms_accepted = fields.Boolean(required=False, load_default=False)
    terms_version = fields.String(required=False, load_default=None)


class UpdateUserPreferencesSchema(Schema):
    preferred_currency = fields.String(
        required=True,
        validate=validate.OneOf(["AOA", "USD", "EUR"]),
    )


class UpdateUserSchema(Schema):
    full_name = fields.String(validate=validate.Length(min=2, max=200))
    role = fields.String(validate=validate.OneOf(UserRole.values()))
    bank_code = fields.String(allow_none=True)
    is_active = fields.Boolean()


class ApproveUserSchema(Schema):
    role = fields.String(
        required=False,
        validate=validate.OneOf([UserRole.FINANCIAL.value, UserRole.USER.value]),
    )
    plan_id = fields.UUID(required=False, allow_none=True)
    access_days = fields.Integer(
        required=False,
        allow_none=True,
        validate=validate.Range(min=1, max=3650),
    )


class ExtendUserAccessSchema(Schema):
    plan_id = fields.UUID(required=True)
    access_days = fields.Integer(required=True, validate=validate.Range(min=1, max=3650))


class UpdateUserRoleSchema(Schema):
    role = fields.String(required=True, validate=validate.OneOf(UserRole.values()))
    bank_code = fields.String(required=False, allow_none=True)


class UserResponseSchema(Schema):
    id = fields.UUID()
    email = fields.Email()
    full_name = fields.String()
    role = fields.String()
    is_active = fields.Boolean()
    preferred_currency = fields.String()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class AuthResponseSchema(Schema):
    user = fields.Nested(UserResponseSchema)
    access_token = fields.String()
    refresh_token = fields.String()
    token_type = fields.String()
    expires_in = fields.Integer()


class AccessLogResponseSchema(Schema):
    id = fields.UUID()
    user_id = fields.UUID(allow_none=True)
    action = fields.String()
    ip_address = fields.String(allow_none=True)
    user_agent = fields.String(allow_none=True)
    metadata = fields.Dict()
    created_at = fields.DateTime()


class PaginatedUsersSchema(Schema):
    items = fields.List(fields.Nested(UserResponseSchema))
    total = fields.Integer()
    limit = fields.Integer()
    offset = fields.Integer()


class PaginatedAccessLogsSchema(Schema):
    items = fields.List(fields.Nested(AccessLogResponseSchema))
    total = fields.Integer()
    limit = fields.Integer()
    offset = fields.Integer()
