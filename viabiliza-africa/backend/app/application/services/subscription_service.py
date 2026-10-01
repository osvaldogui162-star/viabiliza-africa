from uuid import UUID

from app.application.services.plan_capabilities import build_plan_capabilities
from app.domain.entities.admin_config import SubscriptionPlan
from app.domain.entities.user import User
from app.domain.enums.report_type import ReportType
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.domain_exceptions import ValidationError
from app.domain.repositories.admin_config_repository import ISubscriptionRepository


class SubscriptionService:
    """Valida limites e funcionalidades por plano (UC39) — alinhado a /planos."""

    def __init__(self, subscription_repository: ISubscriptionRepository) -> None:
        self._subs = subscription_repository

    def get_user_plan(self, user_id: UUID) -> SubscriptionPlan:
        subscription = self._subs.find_active_subscription(user_id)
        if subscription:
            plan = self._subs.find_plan_by_id(subscription.plan_id)
            if plan and plan.is_active:
                return plan
        free = self._subs.find_plan_by_code("free")
        if free:
            return free
        raise ValidationError("Nenhum plano disponível — contacte o administrador")

    def get_capabilities(self, user_id: UUID) -> dict:
        plan = self.get_user_plan(user_id)
        return build_plan_capabilities(plan)

    def get_usage_snapshot(self, user_id: UUID) -> dict:
        plan = self.get_user_plan(user_id)
        features = plan.features or {}
        max_scraping = features.get("max_scraping_items_monthly")
        if not features.get("scraping"):
            max_scraping = 0

        return {
            "projects_count": self._subs.count_user_projects(user_id),
            "projects_limit": plan.max_projects,
            "scraping_items_this_month": self._subs.count_user_scraping_items_this_month(user_id),
            "scraping_items_limit": max_scraping if features.get("scraping") else 0,
            "collaborators_count": self._subs.count_owner_collaborators(user_id),
            "team_members_limit": plan.max_users,
            "monte_carlo_iterations_limit": plan.max_monte_carlo_iterations,
        }

    def ensure_can_create_project(self, user: User) -> None:
        if user.role == UserRole.ADMIN:
            return
        plan = self.get_user_plan(user.id)
        if plan.max_projects is None:
            return
        count = self._subs.count_user_projects(user.id)
        if count >= plan.max_projects:
            raise ValidationError(
                f"Limite de {plan.max_projects} projectos activos atingido no plano «{plan.name}». "
                "Actualize a sua assinatura em /planos."
            )

    def ensure_can_add_collaborator(self, owner: User, target_user_id: UUID) -> None:
        if owner.role == UserRole.ADMIN:
            return
        plan = self.get_user_plan(owner.id)
        if plan.max_users is None:
            return

        existing_ids = self._subs.find_owner_collaborator_ids(owner.id)
        if target_user_id in existing_ids:
            return

        seats_used = 1 + len(existing_ids)
        if seats_used >= plan.max_users:
            raise ValidationError(
                f"O plano «{plan.name}» permite no máximo {plan.max_users} utilizador(es) "
                f"(inclui o proprietário). Actualize para Business ou superior em /planos."
            )

    def ensure_monte_carlo(self, user: User, iterations: int) -> None:
        if user.role == UserRole.ADMIN:
            return
        plan = self.get_user_plan(user.id)
        features = plan.features or {}
        if not features.get("monte_carlo", False):
            raise ValidationError(
                f"Simulação Monte Carlo não está incluída no plano «{plan.name}»."
            )
        if iterations > plan.max_monte_carlo_iterations:
            raise ValidationError(
                f"O plano «{plan.name}» permite no máximo "
                f"{plan.max_monte_carlo_iterations:,} iterações Monte Carlo. "
                "Reduza as iterações ou actualize o plano."
            )

    def ensure_monte_carlo_iterations(self, user: User, iterations: int) -> None:
        """Alias retrocompatível."""
        self.ensure_monte_carlo(user, iterations)

    def ensure_sensitivity(self, user: User) -> None:
        if user.role == UserRole.ADMIN:
            return
        plan = self.get_user_plan(user.id)
        if not (plan.features or {}).get("sensitivity", False):
            raise ValidationError(
                f"Análise de sensibilidade não está incluída no plano «{plan.name}». "
                "Actualize a sua assinatura em /planos."
            )

    def ensure_feature(self, user: User, feature: str) -> None:
        if user.role == UserRole.ADMIN:
            return
        plan = self.get_user_plan(user.id)
        if not (plan.features or {}).get(feature, False):
            raise ValidationError(
                f"A funcionalidade «{feature}» não está incluída no plano «{plan.name}». "
                "Consulte /planos para comparar pacotes."
            )

    def ensure_report_type(self, user: User, report_type: ReportType) -> None:
        feature_map = {
            ReportType.INTERNATIONAL: "reports_international",
            ReportType.BFA: "reports_bfa",
            ReportType.BDA: "reports_bda",
        }
        self.ensure_feature(user, feature_map[report_type])

    def ensure_bank_api(self, user: User) -> None:
        self.ensure_feature(user, "bank_api")

    def ensure_scraping(self, user: User, *, items_to_add: int = 1) -> None:
        if user.role == UserRole.ADMIN:
            return
        plan = self.get_user_plan(user.id)
        features = plan.features or {}
        if not features.get("scraping", False):
            raise ValidationError(
                f"Ingestão automática e scraping não estão incluídos no plano «{plan.name}». "
                "O plano Starter inclui 50 itens/mês — actualize em /planos."
            )

        limit = features.get("max_scraping_items_monthly")
        if limit is None:
            return

        used = self._subs.count_user_scraping_items_this_month(user.id)
        if used + items_to_add > int(limit):
            raise ValidationError(
                f"Limite mensal de {limit} itens de scraping/ingestão automática atingido "
                f"no plano «{plan.name}» (utilizados: {used}). "
                "Actualize a sua assinatura em /planos."
            )

    def ensure_auto_ingestion(self, user: User, *, catalog_items_count: int) -> None:
        """Pré-validação antes da ingestão automática (até 5 resultados por item)."""
        estimated_results = max(1, catalog_items_count) * 5
        self.ensure_scraping(user, items_to_add=estimated_results)

    def ensure_digital_twin(self, user: User) -> None:
        self.ensure_feature(user, "digital_twin")

    def ensure_esg(self, user: User, *, advanced: bool = False) -> None:
        if user.role == UserRole.ADMIN:
            return
        plan = self.get_user_plan(user.id)
        features = plan.features or {}
        if advanced:
            if not features.get("esg_advanced"):
                raise ValidationError(
                    f"Análise ESG avançada não está incluída no plano «{plan.name}». "
                    "Disponível a partir do plano Business."
                )
            return
        if not (features.get("esg_advanced") or features.get("esg_basic")):
            raise ValidationError(
                f"Análise ESG não está incluída no plano «{plan.name}»."
            )

    def ensure_esg_advanced(self, user: User) -> None:
        self.ensure_esg(user, advanced=True)

    def ensure_sroi(self, user: User) -> None:
        self.ensure_feature(user, "sroi")

    def ensure_erp_billing(self, user: User) -> None:
        self.ensure_feature(user, "erp_billing_integration")
