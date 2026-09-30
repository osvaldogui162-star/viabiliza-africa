from uuid import UUID

from app.application.services.admin_access_policy import AdminAccessPolicy
from app.application.use_cases.admin.mappers import to_template_output
from app.domain.enums.access_action import AccessAction
from app.domain.enums.budget_template_type import BudgetTemplateType
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, ValidationError
from app.domain.repositories.access_log_repository import IAccessLogRepository
from app.domain.repositories.admin_config_repository import IBudgetTemplateRepository


class ListBudgetTemplatesUseCase:
    """UC37 — Listar templates de orçamento."""

    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        repository: IBudgetTemplateRepository,
    ) -> None:
        self._policy = admin_policy
        self._repo = repository

    def execute(self, *, actor_id: UUID) -> dict:
        self._policy.require_admin(actor_id)
        items = self._repo.find_all()
        return {"items": [to_template_output(t) for t in items], "total": len(items)}


class CreateBudgetTemplateUseCase:
    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        repository: IBudgetTemplateRepository,
        access_log_repository: IAccessLogRepository,
    ) -> None:
        self._policy = admin_policy
        self._repo = repository
        self._logs = access_log_repository

    def execute(self, *, actor_id: UUID, **kwargs) -> dict:
        self._policy.require_admin(actor_id)
        if "template_fields" in kwargs:
            kwargs["fields"] = kwargs.pop("template_fields")
        template_type = BudgetTemplateType(kwargs.get("template_type", "both"))
        template = self._repo.create(
            code=kwargs["code"],
            name=kwargs["name"],
            template_type=template_type,
            header_html=kwargs.get("header_html"),
            footer_html=kwargs.get("footer_html"),
            logo_url=kwargs.get("logo_url"),
            primary_color=kwargs.get("primary_color", "#1a5276"),
            fields=kwargs.get("fields") or {},
            is_default=kwargs.get("is_default", False),
            is_active=kwargs.get("is_active", True),
            created_by=actor_id,
        )
        self._logs.create(
            user_id=actor_id,
            action=AccessAction.CONFIG_UPDATED,
            metadata={"type": "budget_template", "code": template.code, "action": "created"},
        )
        return to_template_output(template)


class UpdateBudgetTemplateUseCase:
    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        repository: IBudgetTemplateRepository,
        access_log_repository: IAccessLogRepository,
    ) -> None:
        self._policy = admin_policy
        self._repo = repository
        self._logs = access_log_repository

    def execute(self, *, actor_id: UUID, template_id: UUID, **kwargs) -> dict:
        self._policy.require_admin(actor_id)
        if "template_fields" in kwargs:
            kwargs["fields"] = kwargs.pop("template_fields")
        if self._repo.find_by_id(template_id) is None:
            raise EntityNotFoundError("Template de orçamento", str(template_id))

        if kwargs.get("template_type"):
            kwargs["template_type"] = BudgetTemplateType(kwargs["template_type"])

        template = self._repo.update(template_id, **{k: v for k, v in kwargs.items() if v is not None})
        self._logs.create(
            user_id=actor_id,
            action=AccessAction.CONFIG_UPDATED,
            metadata={"type": "budget_template", "id": str(template_id), "action": "updated"},
        )
        return to_template_output(template)


class SetDefaultBudgetTemplateUseCase:
    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        repository: IBudgetTemplateRepository,
        access_log_repository: IAccessLogRepository,
    ) -> None:
        self._policy = admin_policy
        self._repo = repository
        self._logs = access_log_repository

    def execute(self, *, actor_id: UUID, template_id: UUID) -> dict:
        self._policy.require_admin(actor_id)
        template = self._repo.set_default(template_id)
        self._logs.create(
            user_id=actor_id,
            action=AccessAction.CONFIG_UPDATED,
            metadata={"type": "budget_template", "code": template.code, "action": "set_default"},
        )
        return to_template_output(template)


class DeleteBudgetTemplateUseCase:
    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        repository: IBudgetTemplateRepository,
        access_log_repository: IAccessLogRepository,
    ) -> None:
        self._policy = admin_policy
        self._repo = repository
        self._logs = access_log_repository

    def execute(self, *, actor_id: UUID, template_id: UUID) -> dict:
        self._policy.require_admin(actor_id)
        existing = self._repo.find_by_id(template_id)
        if existing is None:
            raise EntityNotFoundError("Template de orçamento", str(template_id))
        try:
            self._repo.delete(template_id)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        self._logs.create(
            user_id=actor_id,
            action=AccessAction.CONFIG_UPDATED,
            metadata={"type": "budget_template", "code": existing.code, "action": "deleted"},
        )
        return {"message": "Template removido", "code": existing.code}
