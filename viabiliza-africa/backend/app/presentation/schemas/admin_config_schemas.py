from marshmallow import Schema, fields, validate

from app.domain.enums.budget_template_type import BudgetTemplateType
from app.domain.enums.integration_key import IntegrationKey
from app.domain.enums.subscription_status import SubscriptionStatus


class CreateScrapingSourceSchema(Schema):
    code = fields.String(required=True)
    name = fields.String(required=True)
    base_url = fields.String(required=True)
    description = fields.String(required=False)
    country = fields.String(load_default="AO")
    config = fields.Dict(load_default=dict)
    is_active = fields.Boolean(load_default=True)


class UpdateScrapingSourceSchema(Schema):
    name = fields.String(required=False)
    base_url = fields.String(required=False)
    description = fields.String(required=False, allow_none=True)
    country = fields.String(required=False)
    config = fields.Dict(required=False)
    is_active = fields.Boolean(required=False)


class UpdateIntegrationSchema(Schema):
    settings = fields.Dict(required=True)
    is_active = fields.Boolean(load_default=True)


class CreateBudgetTemplateSchema(Schema):
    code = fields.String(required=True)
    name = fields.String(required=True)
    template_type = fields.String(
        load_default="both", validate=validate.OneOf(BudgetTemplateType.values())
    )
    header_html = fields.String(required=False, allow_none=True)
    footer_html = fields.String(required=False, allow_none=True)
    logo_url = fields.String(required=False, allow_none=True)
    primary_color = fields.String(load_default="#1a5276")
    template_fields = fields.Dict(load_default=dict, data_key="fields")
    is_default = fields.Boolean(load_default=False)
    is_active = fields.Boolean(load_default=True)


class UpdateBudgetTemplateSchema(Schema):
    name = fields.String(required=False)
    template_type = fields.String(required=False, validate=validate.OneOf(BudgetTemplateType.values()))
    header_html = fields.String(required=False, allow_none=True)
    footer_html = fields.String(required=False, allow_none=True)
    logo_url = fields.String(required=False, allow_none=True)
    primary_color = fields.String(required=False)
    template_fields = fields.Dict(required=False, data_key="fields")
    is_active = fields.Boolean(required=False)


class CreateSubscriptionPlanSchema(Schema):
    code = fields.String(required=True)
    name = fields.String(required=True)
    description = fields.String(required=False, allow_none=True)
    price_monthly = fields.Decimal(load_default=0)
    price_yearly = fields.Decimal(required=False, allow_none=True)
    currency = fields.String(load_default="USD")
    max_projects = fields.Integer(required=False, allow_none=True)
    max_users = fields.Integer(required=False, allow_none=True)
    max_monte_carlo_iterations = fields.Integer(load_default=1000)
    features = fields.Dict(load_default=dict)
    is_active = fields.Boolean(load_default=True)
    display_order = fields.Integer(load_default=0)


class UpdateSubscriptionPlanSchema(Schema):
    name = fields.String(required=False)
    description = fields.String(required=False, allow_none=True)
    price_monthly = fields.Decimal(required=False)
    price_yearly = fields.Decimal(required=False, allow_none=True)
    currency = fields.String(required=False)
    max_projects = fields.Integer(required=False, allow_none=True)
    max_users = fields.Integer(required=False, allow_none=True)
    max_monte_carlo_iterations = fields.Integer(required=False)
    features = fields.Dict(required=False)
    is_active = fields.Boolean(required=False)
    display_order = fields.Integer(required=False)


class AssignSubscriptionSchema(Schema):
    user_id = fields.UUID(required=True)
    plan_id = fields.UUID(required=True)
    status = fields.String(load_default="active", validate=validate.OneOf(SubscriptionStatus.values()))
    ends_at = fields.DateTime(required=False, allow_none=True)


class UpdateSubscriptionStatusSchema(Schema):
    status = fields.String(required=True, validate=validate.OneOf(SubscriptionStatus.values()))
