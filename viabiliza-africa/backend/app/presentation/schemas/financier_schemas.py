from marshmallow import Schema, fields, validate


class CreateProjectFinancingSchema(Schema):
    bank_code = fields.String(required=True)
    decision = fields.String(
        load_default="pending",
        validate=validate.OneOf(["pending", "approved", "conditional", "rejected"]),
    )
    approved_amount = fields.Decimal(required=True, as_string=True)
    currency = fields.String(load_default="AOA", validate=validate.OneOf(["USD", "EUR", "AOA"]))
    disbursed_amount = fields.Decimal(load_default=None, allow_none=True, as_string=True)
    interest_rate_pct = fields.Decimal(load_default=None, allow_none=True, as_string=True)
    term_months = fields.Integer(load_default=None, allow_none=True)
    submission_id = fields.UUID(load_default=None, allow_none=True)
    notes = fields.String(load_default=None, allow_none=True)


class DecideProjectFinancingSchema(Schema):
    decision = fields.String(
        required=True,
        validate=validate.OneOf(["approved", "conditional", "rejected"]),
    )
    approved_amount = fields.Decimal(load_default=None, allow_none=True, as_string=True)
    disbursed_amount = fields.Decimal(load_default=None, allow_none=True, as_string=True)
    interest_rate_pct = fields.Decimal(load_default=None, allow_none=True, as_string=True)
    term_months = fields.Integer(load_default=None, allow_none=True)
    notes = fields.String(load_default=None, allow_none=True)
