from marshmallow import Schema, fields, validate


class FinancialAssumptionsSchema(Schema):
    annual_revenue_year1 = fields.Decimal(required=False)
    revenue_growth_rate = fields.Decimal(required=False)
    opex_growth_rate = fields.Decimal(required=False)
    tax_rate = fields.Decimal(required=False)
    inflation_rate = fields.Decimal(required=False)
    discount_rate = fields.Decimal(required=False)
    debt_ratio = fields.Decimal(required=False)
    interest_rate = fields.Decimal(required=False)
    equity_amount = fields.Decimal(required=False, allow_none=True)
    depreciation_years = fields.Integer(required=False)
    salvage_value_pct = fields.Decimal(required=False)
    working_capital_pct = fields.Decimal(required=False)
    capex_total = fields.Decimal(required=False, allow_none=True)
    opex_annual = fields.Decimal(required=False, allow_none=True)


class CalculateIndicatorsSchema(Schema):
    assumptions = fields.Nested(FinancialAssumptionsSchema, required=False)


class MonteCarloSchema(Schema):
    iterations = fields.Integer(
        required=False,
        load_default=10000,
        validate=validate.Range(min=1000, max=50000),
    )
    analysis_id = fields.UUID(required=False, allow_none=True)
    variable_std_devs = fields.Dict(
        keys=fields.String(),
        values=fields.Float(),
        required=False,
    )


class SensitivityVariableSchema(Schema):
    key = fields.String(required=True)
    label = fields.String(required=False)
    shock_low_pct = fields.Float(required=False, load_default=-10)
    shock_high_pct = fields.Float(required=False, load_default=10)
    base_value = fields.Float(required=False)


class SensitivitySchema(Schema):
    analysis_id = fields.UUID(required=False, allow_none=True)
    variables = fields.List(fields.Nested(SensitivityVariableSchema), required=False)
