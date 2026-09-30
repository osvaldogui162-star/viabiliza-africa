from marshmallow import Schema, ValidationError, fields, pre_load, validate, validates

from app.domain.catalog.angola_admin_divisions import is_valid_municipality, is_valid_province
from app.domain.enums.country import Country
from app.domain.enums.currency import Currency
from app.domain.enums.financing_bank import FinancingBank
from app.domain.enums.financing_type import FinancingType
from app.domain.enums.project_sector import ProjectSector
from app.domain.enums.project_status import ProjectStatus
from app.domain.enums.share_permission import SharePermission
from app.domain.validators.angola_national import is_valid_bi_format, is_valid_local_phone

_OPTIONAL_BLANK_FIELDS = (
    "description",
    "company_tax_id",
    "discount_rate",
    "bank_code",
    "bank_rate_label",
    "bank_rate_source_url",
    "rep_role",
    "company_address",
    "company_activity",
    "company_phone",
    "company_email",
    "company_website",
    "company_latitude",
    "company_longitude",
    "geocode_source",
    "financing_type",
    "loan_term_months",
    "bank_branch",
)


def _blank_to_none(data: dict) -> dict:
    """Converte strings vazias / NaN / 0 (prazo) em None nos campos opcionais."""
    if not isinstance(data, dict):
        return data
    cleaned = dict(data)
    for key in _OPTIONAL_BLANK_FIELDS:
        if key not in cleaned:
            continue
        value = cleaned[key]
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            cleaned[key] = None
        elif isinstance(value, float) and value != value:  # NaN
            cleaned[key] = None
        elif isinstance(value, str) and value.strip().lower() == "nan":
            cleaned[key] = None

    # Input number vazio no browser costuma chegar como 0
    loan_term = cleaned.get("loan_term_months")
    if loan_term is not None:
        try:
            as_int = int(loan_term)
        except (TypeError, ValueError):
            as_int = None
        if as_int is not None and as_int <= 0:
            cleaned["loan_term_months"] = None

    return cleaned


def _validate_bi_field(value: str) -> None:
    if not is_valid_bi_format(value):
        raise ValidationError(
            "Formato de BI inválido. Use 9 dígitos + 2 letras + 3 dígitos (ex: 006151112LA041)"
        )


def _validate_phone_field(value: str) -> None:
    if value and not is_valid_local_phone(value):
        raise ValidationError("Contacto inválido: 9 dígitos numéricos começando por 9")


class CreateProjectSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=200))
    description = fields.String(allow_none=True, validate=validate.Length(max=5000))
    company_name = fields.String(required=True, validate=validate.Length(min=2, max=200))
    company_tax_id = fields.String(allow_none=True, validate=validate.Length(max=50))
    sector = fields.String(required=True, validate=validate.OneOf(ProjectSector.values()))
    country = fields.String(required=True, validate=validate.OneOf(Country.values()))
    currency = fields.String(required=True, validate=validate.OneOf(Currency.values()))
    investment_amount = fields.Decimal(
        required=True, places=2, as_string=True, validate=validate.Range(min=0.01)
    )
    project_horizon_years = fields.Integer(
        load_default=5, validate=validate.Range(min=1, max=50)
    )
    discount_rate = fields.Decimal(
        allow_none=True, places=3, as_string=True, validate=validate.Range(min=0, max=100)
    )
    bank_code = fields.String(
        allow_none=True, validate=validate.OneOf(FinancingBank.values())
    )
    bank_rate_label = fields.String(allow_none=True, validate=validate.Length(max=300))
    bank_rate_source_url = fields.String(allow_none=True, validate=validate.Length(max=500))
    rep_full_name = fields.String(required=True, validate=validate.Length(min=2, max=200))
    rep_email = fields.Email(required=True)
    rep_id_number = fields.String(required=True, validate=validate.Length(min=14, max=14))
    rep_phone = fields.String(required=True, validate=validate.Length(min=9, max=9))
    rep_role = fields.String(allow_none=True, validate=validate.Length(max=100))
    company_province = fields.String(required=True, validate=validate.Length(max=50))
    company_municipality = fields.String(required=True, validate=validate.Length(max=100))
    company_address = fields.String(allow_none=True, validate=validate.Length(max=1000))
    company_activity = fields.String(allow_none=True, validate=validate.Length(max=300))
    company_phone = fields.String(allow_none=True, validate=validate.Length(max=9))
    company_email = fields.Email(allow_none=True)
    company_website = fields.String(allow_none=True, validate=validate.Length(max=300))
    company_latitude = fields.Decimal(allow_none=True, places=7, as_string=True)
    company_longitude = fields.Decimal(allow_none=True, places=7, as_string=True)
    geocode_verified = fields.Boolean(load_default=False)
    geocode_source = fields.String(allow_none=True, validate=validate.Length(max=30))
    financing_type = fields.String(
        allow_none=True, validate=validate.OneOf(FinancingType.values())
    )
    loan_term_months = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=360))
    bank_branch = fields.String(allow_none=True, validate=validate.Length(max=150))

    @pre_load
    def _clean_optional_blanks(self, data, **kwargs):
        return _blank_to_none(data)

    @validates("rep_id_number")
    def _check_rep_bi(self, value: str, **kwargs) -> None:
        _validate_bi_field(value)

    @validates("rep_phone")
    def _check_rep_phone(self, value: str, **kwargs) -> None:
        _validate_phone_field(value)

    @validates("company_phone")
    def _check_company_phone(self, value: str | None, **kwargs) -> None:
        if value:
            _validate_phone_field(value)

    @staticmethod
    def validate_location(data: dict) -> None:
        province = data.get("company_province")
        municipality = data.get("company_municipality")
        if province and not is_valid_province(province):
            raise ValidationError("Província inválida")
        if province and municipality and not is_valid_municipality(province, municipality):
            raise ValidationError("Município inválido para a província seleccionada")


class UpdateProjectSchema(Schema):
    name = fields.String(validate=validate.Length(min=2, max=200))
    description = fields.String(allow_none=True, validate=validate.Length(max=5000))
    company_name = fields.String(validate=validate.Length(min=2, max=200))
    company_tax_id = fields.String(allow_none=True, validate=validate.Length(max=50))
    sector = fields.String(validate=validate.OneOf(ProjectSector.values()))
    country = fields.String(validate=validate.OneOf(Country.values()))
    currency = fields.String(validate=validate.OneOf(Currency.values()))
    investment_amount = fields.Decimal(
        places=2, as_string=True, validate=validate.Range(min=0.01)
    )
    project_horizon_years = fields.Integer(validate=validate.Range(min=1, max=50))
    discount_rate = fields.Decimal(
        allow_none=True, places=3, as_string=True, validate=validate.Range(min=0, max=100)
    )
    bank_code = fields.String(
        allow_none=True, validate=validate.OneOf(FinancingBank.values())
    )
    bank_rate_label = fields.String(allow_none=True, validate=validate.Length(max=300))
    bank_rate_source_url = fields.String(allow_none=True, validate=validate.Length(max=500))
    rep_full_name = fields.String(validate=validate.Length(min=2, max=200))
    rep_email = fields.Email()
    rep_id_number = fields.String(validate=validate.Length(min=14, max=14))
    rep_phone = fields.String(validate=validate.Length(min=9, max=9))
    rep_role = fields.String(allow_none=True, validate=validate.Length(max=100))
    company_province = fields.String(validate=validate.Length(max=50))
    company_municipality = fields.String(validate=validate.Length(max=100))
    company_address = fields.String(allow_none=True, validate=validate.Length(max=1000))
    company_activity = fields.String(allow_none=True, validate=validate.Length(max=300))
    company_phone = fields.String(allow_none=True, validate=validate.Length(max=9))
    company_email = fields.Email(allow_none=True)
    company_website = fields.String(allow_none=True, validate=validate.Length(max=300))
    company_latitude = fields.Decimal(allow_none=True, places=7, as_string=True)
    company_longitude = fields.Decimal(allow_none=True, places=7, as_string=True)
    geocode_verified = fields.Boolean()
    geocode_source = fields.String(allow_none=True, validate=validate.Length(max=30))
    financing_type = fields.String(
        allow_none=True, validate=validate.OneOf(FinancingType.values())
    )
    loan_term_months = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=360))
    bank_branch = fields.String(allow_none=True, validate=validate.Length(max=150))

    @pre_load
    def _clean_optional_blanks(self, data, **kwargs):
        return _blank_to_none(data)

    @validates("rep_id_number")
    def _check_rep_bi(self, value: str, **kwargs) -> None:
        if value:
            _validate_bi_field(value)

    @validates("rep_phone")
    def _check_rep_phone(self, value: str, **kwargs) -> None:
        if value:
            _validate_phone_field(value)

    @validates("company_phone")
    def _check_company_phone(self, value: str | None, **kwargs) -> None:
        if value:
            _validate_phone_field(value)


class GeocodeLocationSchema(Schema):
    province = fields.String(required=True, validate=validate.Length(max=50))
    municipality = fields.String(required=True, validate=validate.Length(max=100))
    address = fields.String(allow_none=True, validate=validate.Length(max=1000))


class ShareProjectSchema(Schema):
    user_email = fields.Email(required=True)
    permission = fields.String(
        load_default="view",
        validate=validate.OneOf(SharePermission.values()),
    )
