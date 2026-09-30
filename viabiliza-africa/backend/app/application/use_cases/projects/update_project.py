from decimal import Decimal

from app.application.dto.project_dto import ProjectOutput, UpdateProjectInput
from app.application.services.project_access_policy import ProjectAccessPolicy
from app.application.services.shared_project_capability_policy import SharedProjectCapabilityPolicy
from app.domain.enums.project_capability import ProjectCapability
from app.application.use_cases.projects.project_mapper import to_project_output
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
from app.domain.repositories.cost_item_repository import ICostItemRepository
from app.domain.repositories.project_repository import IProjectRepository
from app.domain.repositories.user_repository import IUserRepository
from app.domain.catalog.angola_admin_divisions import is_valid_municipality, is_valid_province
from app.infrastructure.geocoding.location_geocoder import LocationGeocoder


class UpdateProjectUseCase:
    """UC08 — Editar projeto (apenas status Rascunho)."""

    def __init__(
        self,
        user_repository: IUserRepository,
        project_repository: IProjectRepository,
        access_log_repository: IAccessLogRepository,
        access_policy: ProjectAccessPolicy,
        cost_item_repository: ICostItemRepository,
        geocoder: LocationGeocoder | None = None,
        capability_policy: SharedProjectCapabilityPolicy | None = None,
    ) -> None:
        self._users = user_repository
        self._projects = project_repository
        self._access_logs = access_log_repository
        self._policy = access_policy
        self._items = cost_item_repository
        self._geocoder = geocoder or LocationGeocoder()
        self._capabilities = capability_policy

    def execute(self, input_data: UpdateProjectInput) -> ProjectOutput:
        actor = self._users.find_by_id(input_data.actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(input_data.actor_id))

        project = self._projects.find_by_id(input_data.project_id)
        if project is None:
            raise EntityNotFoundError("Projeto", str(input_data.project_id))

        shared_edit = (
            self._capabilities.can(actor, project, ProjectCapability.EDIT_PROJECT.value)
            if self._capabilities
            else False
        )
        if not self._policy.can_edit(actor, project, shared_may_edit=shared_edit):
            if not project.is_editable():
                raise ValidationError(
                    "Projeto só pode ser editado quando o status é Rascunho"
                )
            raise AuthorizationError("Não tem permissão para editar este projeto")

        self._validate_updates(input_data)

        sector = ProjectSector(input_data.sector) if input_data.sector else None
        country = Country(input_data.country.upper()) if input_data.country else None
        currency = Currency(input_data.currency.upper()) if input_data.currency else None

        lat = input_data.company_latitude
        lng = input_data.company_longitude
        geocode_verified = input_data.geocode_verified
        geocode_source = input_data.geocode_source

        province = input_data.company_province or (
            project.company_province if input_data.company_municipality else None
        )
        municipality = input_data.company_municipality
        address = input_data.company_address

        if province and municipality:
            if lat is None and lng is None and geocode_verified is None:
                geo = self._geocoder.geocode(
                    province_code=province,
                    municipality_code=municipality,
                    address=address,
                )
                lat = geo.latitude
                lng = geo.longitude
                geocode_verified = geo.verified
                geocode_source = geo.source

        updated = self._projects.update(
            input_data.project_id,
            name=input_data.name.strip() if input_data.name else None,
            description=input_data.description,
            company_name=input_data.company_name.strip() if input_data.company_name else None,
            company_tax_id=input_data.company_tax_id,
            sector=sector,
            country=country,
            currency=currency,
            investment_amount=input_data.investment_amount,
            project_horizon_years=input_data.project_horizon_years,
            discount_rate=input_data.discount_rate,
            bank_code=input_data.bank_code,
            bank_rate_label=input_data.bank_rate_label,
            bank_rate_source_url=input_data.bank_rate_source_url,
            rep_full_name=input_data.rep_full_name.strip() if input_data.rep_full_name else None,
            rep_email=input_data.rep_email.strip() if input_data.rep_email else None,
            rep_id_number=input_data.rep_id_number.strip() if input_data.rep_id_number else None,
            rep_phone=input_data.rep_phone.strip() if input_data.rep_phone else None,
            rep_role=input_data.rep_role.strip() if input_data.rep_role else None,
            company_province=input_data.company_province,
            company_municipality=input_data.company_municipality,
            company_address=input_data.company_address,
            company_activity=input_data.company_activity,
            company_phone=input_data.company_phone,
            company_email=input_data.company_email,
            company_website=input_data.company_website,
            company_latitude=Decimal(str(lat)) if lat is not None else None,
            company_longitude=Decimal(str(lng)) if lng is not None else None,
            geocode_verified=geocode_verified,
            geocode_source=geocode_source,
            financing_type=input_data.financing_type,
            loan_term_months=input_data.loan_term_months,
            bank_branch=input_data.bank_branch.strip() if input_data.bank_branch else None,
        )

        self._access_logs.create(
            user_id=actor.id,
            action=AccessAction.PROJECT_UPDATED,
            ip_address=input_data.ip_address,
            user_agent=input_data.user_agent,
            metadata={"project_id": str(updated.id)},
        )

        owner = self._users.find_by_id(updated.owner_id)
        cost_items = self._items.find_by_project(updated.id)
        return to_project_output(
            updated,
            owner=owner,
            actor_id=actor.id,
            cost_items=cost_items,
        )

    def _validate_updates(self, input_data: UpdateProjectInput) -> None:
        if input_data.sector and not ProjectSector.is_valid(input_data.sector):
            raise ValidationError(f"Setor inválido. Valores: {', '.join(ProjectSector.values())}")
        if input_data.country and not Country.is_valid(input_data.country):
            raise ValidationError(f"País inválido. Valores: {', '.join(Country.values())}")
        if input_data.currency and not Currency.is_valid(input_data.currency):
            raise ValidationError(f"Moeda inválida. Valores: {', '.join(Currency.values())}")
        if input_data.investment_amount is not None and input_data.investment_amount <= Decimal("0"):
            raise ValidationError("Montante de investimento deve ser superior a zero")
        if input_data.project_horizon_years is not None and (
            input_data.project_horizon_years < 1 or input_data.project_horizon_years > 50
        ):
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
        if input_data.company_province and not is_valid_province(input_data.company_province):
            raise ValidationError("Província inválida")
        if input_data.company_province and input_data.company_municipality and not is_valid_municipality(
            input_data.company_province, input_data.company_municipality
        ):
            raise ValidationError("Município inválido para a província seleccionada")
        if input_data.financing_type and not FinancingType.is_valid(input_data.financing_type):
            raise ValidationError(
                f"Tipo de financiamento inválido. Valores: {', '.join(FinancingType.values())}"
            )
