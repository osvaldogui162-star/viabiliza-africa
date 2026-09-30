from decimal import Decimal

from app.application.dto.project_dto import CreateProjectInput, ProjectOutput
from app.application.services.project_access_policy import ProjectAccessPolicy
from app.application.services.subscription_service import SubscriptionService
from app.application.use_cases.projects.project_mapper import to_project_output
from app.domain.catalog.angola_admin_divisions import (
    is_valid_municipality,
    is_valid_province,
)
from app.domain.enums.access_action import AccessAction
from app.domain.enums.country import Country
from app.domain.enums.currency import Currency
from app.domain.enums.financing_bank import FinancingBank
from app.domain.enums.financing_type import FinancingType
from app.domain.enums.project_sector import ProjectSector
from app.domain.exceptions.domain_exceptions import (
    AuthorizationError,
    EntityNotFoundError,
    ValidationError,
)
from app.domain.repositories.access_log_repository import IAccessLogRepository
from app.domain.repositories.project_repository import IProjectRepository
from app.domain.repositories.user_repository import IUserRepository
from app.domain.validators.angola_national import validate_bi_format, validate_local_phone
from app.infrastructure.external.angola_api_client import AngolaApiClient
from app.infrastructure.geocoding.location_geocoder import LocationGeocoder


class CreateProjectUseCase:
    """UC06 — Criar novo projeto."""

    def __init__(
        self,
        user_repository: IUserRepository,
        project_repository: IProjectRepository,
        access_log_repository: IAccessLogRepository,
        access_policy: ProjectAccessPolicy,
        subscription_service: SubscriptionService | None = None,
        geocoder: LocationGeocoder | None = None,
        angola_api: AngolaApiClient | None = None,
    ) -> None:
        self._users = user_repository
        self._projects = project_repository
        self._access_logs = access_log_repository
        self._policy = access_policy
        self._subscriptions = subscription_service
        self._geocoder = geocoder or LocationGeocoder()
        self._angola = angola_api or AngolaApiClient()

    def execute(self, input_data: CreateProjectInput) -> ProjectOutput:
        actor = self._users.find_by_id(input_data.actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(input_data.actor_id))
        if not self._policy.can_create(actor):
            raise AuthorizationError("Apenas administradores e analistas podem criar projetos")

        if self._subscriptions:
            self._subscriptions.ensure_can_create_project(actor)

        self._validate(input_data)

        try:
            normalized_bi = validate_bi_format(input_data.rep_id_number or "")
            normalized_rep_phone = validate_local_phone(
                input_data.rep_phone or "", field_label="Contacto do representante"
            )
            normalized_company_phone = None
            if input_data.company_phone and input_data.company_phone.strip():
                normalized_company_phone = validate_local_phone(
                    input_data.company_phone, field_label="Telefone da empresa"
                )
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        lat = input_data.company_latitude
        lng = input_data.company_longitude
        geocode_verified = input_data.geocode_verified
        geocode_source = input_data.geocode_source

        if input_data.company_province and input_data.company_municipality:
            if not geocode_verified or lat is None or lng is None:
                geo = self._geocoder.geocode(
                    province_code=input_data.company_province,
                    municipality_code=input_data.company_municipality,
                    address=input_data.company_address,
                )
                lat = Decimal(str(geo.latitude))
                lng = Decimal(str(geo.longitude))
                geocode_verified = geo.verified
                geocode_source = geo.source

        project = self._projects.create(
            owner_id=actor.id,
            name=input_data.name.strip(),
            description=input_data.description.strip() if input_data.description else None,
            company_name=input_data.company_name.strip(),
            company_tax_id=input_data.company_tax_id.strip() if input_data.company_tax_id else None,
            sector=ProjectSector(input_data.sector),
            country=Country(input_data.country.upper()),
            currency=Currency(input_data.currency.upper()),
            investment_amount=input_data.investment_amount,
            project_horizon_years=input_data.project_horizon_years,
            discount_rate=input_data.discount_rate,
            bank_code=input_data.bank_code,
            bank_rate_label=input_data.bank_rate_label,
            bank_rate_source_url=input_data.bank_rate_source_url,
            rep_full_name=input_data.rep_full_name.strip() if input_data.rep_full_name else None,
            rep_email=input_data.rep_email.strip() if input_data.rep_email else None,
            rep_id_number=normalized_bi,
            rep_phone=normalized_rep_phone,
            rep_role=input_data.rep_role.strip() if input_data.rep_role else None,
            company_province=input_data.company_province,
            company_municipality=input_data.company_municipality,
            company_address=input_data.company_address.strip() if input_data.company_address else None,
            company_activity=input_data.company_activity.strip() if input_data.company_activity else None,
            company_phone=normalized_company_phone,
            company_email=input_data.company_email.strip() if input_data.company_email else None,
            company_website=input_data.company_website.strip() if input_data.company_website else None,
            company_latitude=lat,
            company_longitude=lng,
            geocode_verified=geocode_verified,
            geocode_source=geocode_source,
            financing_type=input_data.financing_type,
            loan_term_months=input_data.loan_term_months,
            bank_branch=input_data.bank_branch.strip() if input_data.bank_branch else None,
        )

        self._access_logs.create(
            user_id=actor.id,
            action=AccessAction.PROJECT_CREATED,
            ip_address=input_data.ip_address,
            user_agent=input_data.user_agent,
            metadata={"project_id": str(project.id), "name": project.name},
        )

        return to_project_output(project, owner=actor, actor_id=actor.id)

    def _validate(self, input_data: CreateProjectInput) -> None:
        if not input_data.name.strip():
            raise ValidationError("Nome do projeto é obrigatório")
        if not input_data.company_name.strip():
            raise ValidationError("Nome da empresa é obrigatório")
        if not ProjectSector.is_valid(input_data.sector):
            raise ValidationError(f"Setor inválido. Valores: {', '.join(ProjectSector.values())}")
        if not Country.is_valid(input_data.country):
            raise ValidationError(f"País inválido. Valores: {', '.join(Country.values())}")
        if not Currency.is_valid(input_data.currency):
            raise ValidationError(f"Moeda inválida. Valores: {', '.join(Currency.values())}")
        if input_data.investment_amount <= Decimal("0"):
            raise ValidationError("Montante de investimento deve ser superior a zero")
        if input_data.project_horizon_years < 1 or input_data.project_horizon_years > 50:
            raise ValidationError("Horizonte do projeto deve estar entre 1 e 50 anos")
        if input_data.discount_rate is not None and (
            input_data.discount_rate < Decimal("0")
            or input_data.discount_rate > Decimal("100")
        ):
            raise ValidationError("Taxa de desconto deve estar entre 0 e 100")
        if input_data.bank_code and not FinancingBank.is_valid(input_data.bank_code):
            raise ValidationError(
                f"Banco inválido. Valores: {', '.join(FinancingBank.values())}"
            )
        if not input_data.rep_full_name or not input_data.rep_full_name.strip():
            raise ValidationError("Nome do representante é obrigatório")
        if not input_data.rep_email or not input_data.rep_email.strip():
            raise ValidationError("Email do representante é obrigatório")
        if not input_data.rep_id_number or not input_data.rep_id_number.strip():
            raise ValidationError("Número do BI do representante é obrigatório")
        if not input_data.rep_phone or not input_data.rep_phone.strip():
            raise ValidationError("Contacto do representante é obrigatório")

        try:
            bi_result = self._angola.validate_bi(input_data.rep_id_number)
            if not bi_result.valid:
                raise ValidationError(bi_result.message)

            phone_result = self._angola.validate_phone(input_data.rep_phone)
            if not phone_result.valid:
                raise ValidationError(phone_result.message)

            if input_data.company_phone and input_data.company_phone.strip():
                company_phone_result = self._angola.validate_phone(
                    input_data.company_phone, optional=True
                )
                if not company_phone_result.valid:
                    raise ValidationError(company_phone_result.message)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        if not input_data.company_province or not is_valid_province(input_data.company_province):
            raise ValidationError("Província da empresa é obrigatória e deve ser válida")
        if not input_data.company_municipality or not is_valid_municipality(
            input_data.company_province, input_data.company_municipality
        ):
            raise ValidationError("Município da empresa é obrigatório e deve ser válido")
        if input_data.financing_type and not FinancingType.is_valid(input_data.financing_type):
            raise ValidationError(
                f"Tipo de financiamento inválido. Valores: {', '.join(FinancingType.values())}"
            )
        if input_data.loan_term_months is not None and (
            input_data.loan_term_months < 1 or input_data.loan_term_months > 360
        ):
            raise ValidationError("Prazo do financiamento deve estar entre 1 e 360 meses")
