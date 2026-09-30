from marshmallow import Schema, fields, validate

from app.domain.enums.bank_code import BankCode
from app.domain.enums.report_language import ReportLanguage
from app.domain.enums.report_type import ReportType


class GenerateReportSchema(Schema):
    report_type = fields.String(required=True, validate=validate.OneOf(ReportType.values()))
    language = fields.String(load_default="pt", validate=validate.OneOf(ReportLanguage.values()))
    currency = fields.String(load_default="AOA", validate=validate.OneOf(["USD", "EUR", "AOA"]))
    print_optimized = fields.Boolean(load_default=False)


class SendReportEmailSchema(Schema):
    to_email = fields.Email(required=True)
    subject = fields.String(required=False, validate=validate.Length(min=3, max=200))
    message = fields.String(required=False, validate=validate.Length(max=4000))


class ShareReportWhatsAppSchema(Schema):
    phone = fields.String(required=False)


class SubmitBankReportSchema(Schema):
    bank_code = fields.String(required=True, validate=validate.OneOf(BankCode.values()))
