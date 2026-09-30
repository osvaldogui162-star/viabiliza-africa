from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from app.application.interfaces.hash_service import IHashService
from app.application.services.billing_api_key import (
    api_key_hint,
    generate_billing_api_key,
    hash_billing_api_key,
)
from app.application.services.financier_portfolio_loader import FinancierPortfolioLoader
from app.application.services.project_access_policy import ProjectAccessPolicy
from app.application.services.terminal_monitoring_service import (
    build_terminal_panel,
    forecast_from_analysis,
    hash_billing_payload,
    billing_connection_steps,
)
from app.domain.exceptions.domain_exceptions import (
    AuthenticationError,
    AuthorizationError,
    EntityNotFoundError,
    ValidationError,
)
from app.domain.repositories.analysis_repository import IFinancialAnalysisRepository
from app.domain.repositories.billing_integration_repository import IProjectBillingIntegrationRepository
from app.domain.repositories.project_repository import IProjectRepository
from app.domain.repositories.user_repository import IUserRepository

TERMINAL_SYNC_PATH = "/api/v1/terminal/billing/sync"


def _integration_output(row) -> dict:
    return {
        "project_id": str(row.project_id),
        "erp_label": row.erp_label,
        "connection_status": row.connection_status,
        "api_key_hint": row.api_key_hint,
        "has_api_key": bool(row.api_key_hash),
        "last_sync_at": row.last_sync_at.isoformat() if row.last_sync_at else None,
        "last_hash": row.last_hash,
        "latest_snapshot": row.latest_snapshot,
        "sync_endpoint": TERMINAL_SYNC_PATH,
        "sync_header": "X-Terminal-Api-Key",
    }


def _demo_payload(project, analysis_repo: IFinancialAnalysisRepository | None) -> dict:
    analyses = analysis_repo.find_by_project(project.id, limit=1) if analysis_repo else []
    forecast = forecast_from_analysis(analyses[0] if analyses else None, project)
    return {
        "revenue": float(forecast["revenue"] * Decimal("0.92")),
        "gross_margin_pct": float(forecast["gross_margin_pct"] * Decimal("0.91")),
        "ebitda": float(forecast["ebitda"] * Decimal("0.9")),
        "cash_balance": float(forecast["cash_balance"] * Decimal("0.85")),
        "receivables": float(forecast["receivables"] * Decimal("1.05")),
        "payables": float(forecast["payables"] * Decimal("1.08")),
        "total_debt": float(forecast["total_debt"]),
        "debt_service": float(forecast["debt_service"] * Decimal("1.02")),
        "production_units": float(forecast["production_units"] * Decimal("0.95")),
        "capacity_used_pct": float(forecast["capacity_used_pct"] * Decimal("0.94")),
        "productivity": float(forecast["productivity"] * Decimal("1.03")),
    }


def _normalize_sync_payload(
    project,
    payload: dict,
    analysis_repo: IFinancialAnalysisRepository | None,
) -> dict:
    if not isinstance(payload, dict):
        raise ValidationError("Payload de sincronização inválido")
    if not payload or payload.get("source") == "manual_demo":
        return _demo_payload(project, analysis_repo)
    required = ("revenue", "ebitda", "cash_balance")
    if not any(k in payload for k in required):
        raise ValidationError("Payload deve incluir indicadores financeiros (ex.: revenue, ebitda, cash_balance)")
    return payload


class GetProjectBillingIntegrationUseCase:
    def __init__(
        self,
        users: IUserRepository,
        projects: IProjectRepository,
        billing: IProjectBillingIntegrationRepository,
        project_access: ProjectAccessPolicy,
    ) -> None:
        self._users = users
        self._projects = projects
        self._billing = billing
        self._project_access = project_access

    def execute(self, *, actor_id: UUID, project_id: UUID) -> dict:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))
        project = self._projects.find_by_id(project_id)
        if project is None:
            raise EntityNotFoundError("Projeto", str(project_id))
        if not self._project_access.can_view(actor, project):
            raise AuthorizationError("Sem acesso ao projecto")

        row = self._billing.find_by_project(project_id)
        if row is None:
            return {
                "integration": None,
                "steps": [],
                "sync_endpoint": TERMINAL_SYNC_PATH,
                "sync_header": "X-Terminal-Api-Key",
            }

        return {
            "integration": _integration_output(row),
            "steps": billing_connection_steps(row),
            "sync_endpoint": TERMINAL_SYNC_PATH,
            "sync_header": "X-Terminal-Api-Key",
        }


class ConfigureProjectBillingIntegrationUseCase:
    def __init__(
        self,
        users: IUserRepository,
        projects: IProjectRepository,
        billing: IProjectBillingIntegrationRepository,
        project_access: ProjectAccessPolicy,
        hash_service: IHashService,
    ) -> None:
        self._users = users
        self._projects = projects
        self._billing = billing
        self._project_access = project_access
        self._hash = hash_service

    def execute(self, *, actor_id: UUID, project_id: UUID, erp_label: str) -> dict:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))
        project = self._projects.find_by_id(project_id)
        if project is None:
            raise EntityNotFoundError("Projeto", str(project_id))
        if not self._project_access.can_edit(actor, project):
            raise AuthorizationError("Sem permissão para configurar integração")

        label = (erp_label or "").strip()
        if len(label) < 2:
            raise ValidationError("Indique o sistema de facturação/ERP")

        raw_key = generate_billing_api_key()
        key_hash = hash_billing_api_key(raw_key, self._hash)
        hint = api_key_hint(raw_key)
        row = self._billing.upsert(
            project_id=project_id,
            erp_label=label,
            connection_status="authenticated",
            api_key_hint=hint,
            api_key_hash=key_hash,
        )

        return {
            "integration": _integration_output(row),
            "steps": billing_connection_steps(row),
            "api_key": raw_key,
            "api_key_show_once": True,
        }


class RegenerateProjectBillingApiKeyUseCase:
    def __init__(
        self,
        users: IUserRepository,
        projects: IProjectRepository,
        billing: IProjectBillingIntegrationRepository,
        project_access: ProjectAccessPolicy,
        hash_service: IHashService,
    ) -> None:
        self._users = users
        self._projects = projects
        self._billing = billing
        self._project_access = project_access
        self._hash = hash_service

    def execute(self, *, actor_id: UUID, project_id: UUID) -> dict:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))
        project = self._projects.find_by_id(project_id)
        if project is None:
            raise EntityNotFoundError("Projeto", str(project_id))
        if not self._project_access.can_edit(actor, project):
            raise AuthorizationError("Sem permissão")

        existing = self._billing.find_by_project(project_id)
        if existing is None:
            raise ValidationError("Configure primeiro a integração de facturação")

        raw_key = generate_billing_api_key()
        row = self._billing.upsert(
            project_id=project_id,
            api_key_hint=api_key_hint(raw_key),
            api_key_hash=hash_billing_api_key(raw_key, self._hash),
            connection_status="authenticated",
        )
        return {
            "integration": _integration_output(row),
            "api_key": raw_key,
            "api_key_show_once": True,
        }


class SyncProjectBillingIntegrationUseCase:
    def __init__(
        self,
        users: IUserRepository,
        projects: IProjectRepository,
        billing: IProjectBillingIntegrationRepository,
        project_access: ProjectAccessPolicy,
        analysis: IFinancialAnalysisRepository | None = None,
    ) -> None:
        self._users = users
        self._projects = projects
        self._billing = billing
        self._project_access = project_access
        self._analysis = analysis

    def execute(self, *, actor_id: UUID, project_id: UUID, payload: dict) -> dict:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))
        project = self._projects.find_by_id(project_id)
        if project is None:
            raise EntityNotFoundError("Projeto", str(project_id))
        if not self._project_access.can_edit(actor, project):
            raise AuthorizationError("Sem permissão para sincronizar")

        normalized = _normalize_sync_payload(project, payload, self._analysis)
        digest = hash_billing_payload(normalized)
        row = self._billing.record_sync(
            project_id=project_id,
            payload=normalized,
            payload_hash=digest,
            connection_status="active",
        )
        return {"integration": _integration_output(row), "payload_hash": digest}


class SyncBillingViaApiKeyUseCase:
    def __init__(
        self,
        projects: IProjectRepository,
        billing: IProjectBillingIntegrationRepository,
        hash_service: IHashService,
        analysis: IFinancialAnalysisRepository | None = None,
    ) -> None:
        self._projects = projects
        self._billing = billing
        self._hash = hash_service
        self._analysis = analysis

    def execute(self, *, api_key: str, payload: dict) -> dict:
        key_hash = hash_billing_api_key(api_key, self._hash)
        integration = self._billing.find_by_api_key_hash(key_hash)
        if integration is None:
            raise AuthenticationError("API Key inválida")

        project = self._projects.find_by_id(integration.project_id)
        if project is None:
            raise AuthenticationError("API Key inválida")

        normalized = _normalize_sync_payload(project, payload, self._analysis)
        digest = hash_billing_payload(normalized)
        row = self._billing.record_sync(
            project_id=integration.project_id,
            payload=normalized,
            payload_hash=digest,
            connection_status="active",
        )
        return {
            "project_id": str(integration.project_id),
            "payload_hash": digest,
            "connection_status": row.connection_status,
            "last_sync_at": row.last_sync_at.isoformat() if row.last_sync_at else None,
        }


class ListFinancierBillingIntegrationsUseCase:
    def __init__(
        self,
        loader: FinancierPortfolioLoader,
        billing: IProjectBillingIntegrationRepository,
    ) -> None:
        self._loader = loader
        self._billing = billing

    def execute(self, *, actor_id: UUID) -> dict:
        actor, visible, _ = self._loader.load_visible_financings(actor_id)
        if not self._loader._policy.can_list_portfolio(actor):
            raise AuthorizationError("Sem acesso")

        project_ids = [f.project_id for f in visible]
        by_project = self._billing.find_by_projects(project_ids)
        items = []
        for f in visible:
            project = self._loader._projects.find_by_id(f.project_id)
            if project is None:
                continue
            integration = by_project.get(f.project_id)
            items.append(
                {
                    "financing_id": str(f.id),
                    "project_id": str(f.project_id),
                    "project_name": project.name,
                    "company_name": project.company_name,
                    "integration": _integration_output(integration) if integration else None,
                    "steps": billing_connection_steps(integration),
                }
            )
        connected = sum(
            1
            for i in items
            if i.get("integration") and i["integration"]["connection_status"] == "active"
        )
        return {"items": items, "total": len(items), "connected_count": connected}


class ExportFinancierCreditReportUseCase:
    """Relatório mensal para comité de crédito (Terminal — previsto vs. real)."""

    def __init__(
        self,
        loader: FinancierPortfolioLoader,
        billing: IProjectBillingIntegrationRepository,
        analysis: IFinancialAnalysisRepository,
    ) -> None:
        self._loader = loader
        self._billing = billing
        self._analysis = analysis

    def execute(self, *, actor_id: UUID) -> dict:
        actor, visible, bank_filter = self._loader.load_visible_financings(actor_id)
        if not self._loader._policy.can_list_portfolio(actor):
            raise AuthorizationError("Sem acesso")

        project_ids = [f.project_id for f in visible]
        by_billing = self._billing.find_by_projects(project_ids)
        rows: list[dict] = []

        for f in visible:
            project = self._loader._projects.find_by_id(f.project_id)
            if project is None:
                continue
            enriched = self._loader.enrich_item(f, project)
            integration = by_billing.get(f.project_id)
            analyses = self._analysis.find_by_project(f.project_id, limit=1)
            terminal = build_terminal_panel(
                project=project,
                analysis=analyses[0] if analyses else None,
                integration=integration,
                physical_pct=float(enriched.get("physical_pct") or 0),
            )
            rev_row = next((i for i in terminal["indicators"] if i["key"] == "revenue"), None)
            rows.append(
                {
                    "projecto": project.name,
                    "empresa": project.company_name,
                    "setor": project.sector.value,
                    "banco": f.bank_code,
                    "valor_financiado": str(f.approved_amount),
                    "moeda": f.currency,
                    "estado_carteira": enriched.get("monitoring_status"),
                    "desvio_receita_pct": terminal.get("deviation_pct"),
                    "risco_terminal": terminal.get("risk_level"),
                    "score_risco": terminal.get("risk_score", {}).get("value"),
                    "facturacao_ligada": "sim" if integration and integration.connection_status == "active" else "nao",
                    "receita_prevista": rev_row["forecast"] if rev_row else None,
                    "receita_real": rev_row["real"] if rev_row else None,
                    "ultima_sync": integration.last_sync_at.isoformat()
                    if integration and integration.last_sync_at
                    else None,
                    "alertas_terminal": len(terminal.get("alerts") or []),
                }
            )

        return {
            "report_type": "credit_committee",
            "report_title": "Terminal Viabiliza+África — Relatório de Crédito",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "viewer_bank": bank_filter,
            "rows": rows,
            "summary": {
                "projects_count": len(rows),
                "high_risk_count": sum(1 for r in rows if r.get("risco_terminal") == "high"),
                "billing_connected": sum(1 for r in rows if r.get("facturacao_ligada") == "sim"),
            },
        }
