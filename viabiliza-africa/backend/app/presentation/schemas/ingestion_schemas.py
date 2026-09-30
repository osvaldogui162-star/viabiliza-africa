from marshmallow import Schema, fields, validate

from app.domain.enums.cost_item_type import CostItemType


class CreateCostItemSchema(Schema):
    item_type = fields.String(required=True, validate=validate.OneOf(CostItemType.values()))
    category = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(required=True, validate=validate.Length(min=1, max=2000))
    quantity = fields.Decimal(required=True, places=4, as_string=True, validate=validate.Range(min=0.0001))
    unit = fields.String(load_default="un", validate=validate.Length(max=30))
    unit_price = fields.Decimal(required=True, places=2, as_string=True, validate=validate.Range(min=0))
    supplier_nif = fields.String(allow_none=True, validate=validate.Length(max=50))
    supplier_name = fields.String(allow_none=True, validate=validate.Length(max=200))


class UpdateCostItemSchema(Schema):
    category = fields.String(validate=validate.Length(min=1, max=100))
    description = fields.String(validate=validate.Length(min=1, max=2000))
    quantity = fields.Decimal(places=4, as_string=True, validate=validate.Range(min=0.0001))
    unit = fields.String(validate=validate.Length(max=30))
    unit_price = fields.Decimal(places=2, as_string=True, validate=validate.Range(min=0))


class ExecuteScrapingSchema(Schema):
    search_query = fields.String(required=True, validate=validate.Length(min=2, max=300))
    sources = fields.List(fields.String(), load_default=None)


class SelectSupplierSchema(Schema):
    item_type = fields.String(load_default="capex", validate=validate.OneOf(CostItemType.values()))
    category = fields.String(load_default="Equipamento", validate=validate.Length(max=100))
    quantity = fields.Decimal(load_default="1", places=4, as_string=True)


class GenerateBudgetSchema(Schema):
    title = fields.String(load_default="Orçamento Rastreável", validate=validate.Length(max=200))


class GenerateProformaSchema(Schema):
    client_name = fields.String(allow_none=True, validate=validate.Length(min=2, max=200))
    client_tax_id = fields.String(allow_none=True, validate=validate.Length(max=50))
    notes = fields.String(allow_none=True, validate=validate.Length(max=2000))


class AutoIngestionItemOverrideSchema(Schema):
    key = fields.String(required=True, validate=validate.Length(min=1, max=80))
    quantity = fields.Decimal(
        required=True, places=4, as_string=True, validate=validate.Range(min=0.0001)
    )
    include = fields.Boolean(load_default=True)


class RunAutoIngestionSchema(Schema):
    sources = fields.List(fields.String(), load_default=None)
    replace_existing = fields.Boolean(load_default=False)
    generate_proforma = fields.Boolean(load_default=True)
    items = fields.List(
        fields.Nested(AutoIngestionItemOverrideSchema),
        load_default=None,
    )