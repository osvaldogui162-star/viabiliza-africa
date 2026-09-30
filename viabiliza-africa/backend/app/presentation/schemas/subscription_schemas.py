from marshmallow import Schema, fields, validate


class CheckoutQuerySchema(Schema):
    plan_code = fields.Str(required=True, validate=validate.Length(min=2, max=30))
    billing_cycle = fields.Str(
        load_default="quarterly",
        validate=validate.OneOf(["quarterly", "semiannual", "yearly", "monthly"]),
    )
    currency = fields.Str(
        load_default="USD",
        validate=validate.OneOf(["USD", "AOA"]),
    )


class InitiateAppyPayPaymentSchema(Schema):
    plan_code = fields.Str(required=True, validate=validate.Length(min=2, max=30))
    billing_cycle = fields.Str(
        load_default="quarterly",
        validate=validate.OneOf(["quarterly", "semiannual", "yearly", "monthly"]),
    )
    payment_method = fields.Str(required=True, validate=validate.OneOf(["gpo", "ref"]))
    phone_number = fields.Str(load_default=None)


class SubscribeSchema(Schema):
    plan_code = fields.Str(required=True, validate=validate.Length(min=2, max=30))
    billing_cycle = fields.Str(
        load_default="quarterly",
        validate=validate.OneOf(["quarterly", "semiannual", "yearly", "monthly"]),
    )
    currency = fields.Str(
        load_default="AOA",
        validate=validate.OneOf(["USD", "AOA"]),
    )
    payment_method = fields.Str(required=False)
