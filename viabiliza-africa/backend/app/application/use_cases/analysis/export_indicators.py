from uuid import UUID

from app.application.interfaces.financial_calculator import FinancialAnalysisResult, IndicatorResult
from app.application.services.analysis_access_policy import AnalysisAccessPolicy
from app.application.services.project_context_resolver import ProjectContextResolver
from app.domain.exceptions.domain_exceptions import AuthorizationError, EntityNotFoundError
from app.domain.repositories.analysis_repository import (
    IFinancialAnalysisRepository,
    ISensitivityRepository,
)
from app.domain.repositories.cost_item_repository import ICostItemRepository
from app.domain.value_objects.financial_assumptions import CashFlowProjection
from app.infrastructure.excel.indicators_exporter import IndicatorsExcelExporter


class ExportIndicatorsUseCase:
    """UC23 — Exportar estudo de viabilidade Excel (modelo 11 planilhas)."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        analysis_policy: AnalysisAccessPolicy,
        analysis_repository: IFinancialAnalysisRepository,
        exporter: IndicatorsExcelExporter,
        cost_item_repository: ICostItemRepository,
        sensitivity_repository: ISensitivityRepository | None = None,
    ) -> None:
        self._ctx = context_resolver
        self._policy = analysis_policy
        self._analysis_repo = analysis_repository
        self._exporter = exporter
        self._items = cost_item_repository
        self._sensitivity = sensitivity_repository

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        analysis_id: UUID | None = None,
        language: str = "pt",
    ) -> tuple[bytes, str]:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_execute_analysis(ctx.actor, ctx.project):
            raise AuthorizationError("Não tem permissão para exportar indicadores")

        if analysis_id:
            stored = self._analysis_repo.find_by_id(analysis_id)
        else:
            analyses = self._analysis_repo.find_by_project(project_id, limit=1)
            stored = analyses[0] if analyses else None

        if stored is None or stored.project_id != project_id:
            raise EntityNotFoundError("Análise", str(analysis_id or project_id))

        result = self._to_result(stored)
        date_tag = stored.created_at.strftime("%Y-%m-%d")
        filename = f"ViabilizA_Estudo_Viabilidade_{date_tag}.xlsx"

        cost_items = []
        for item in self._items.find_by_project(project_id):
            cost_items.append(
                {
                    "item_type": item.item_type.value if item.item_type else "",
                    "category": item.category,
                    "description": item.description,
                    "quantity": float(item.quantity),
                    "unit_price": float(item.unit_price),
                    "total_amount": float(item.total_amount),
                    "unit": item.unit,
                }
            )

        sensitivity_payload: dict | None = None
        if self._sensitivity is not None:
            try:
                sens_list = self._sensitivity.find_by_project(project_id, limit=1)
                if sens_list:
                    sens = sens_list[0]
                    sensitivity_payload = {
                        "items": getattr(sens, "results", None)
                        or getattr(sens, "variables", None)
                        or [],
                    }
                    if isinstance(getattr(sens, "results", None), dict):
                        sensitivity_payload = sens.results
            except Exception:
                sensitivity_payload = None

        investment = float(ctx.project.investment_amount or 0)
        horizon = int(getattr(ctx.project, "project_horizon_years", None) or 5)

        content = self._exporter.export(
            result,
            project_name=ctx.project.name,
            company_name=ctx.project.company_name,
            sector=ctx.project.sector.value if ctx.project.sector else None,
            country=ctx.project.country.value if ctx.project.country else None,
            currency=ctx.project.currency.value if ctx.project.currency else "AOA",
            assumptions=stored.assumptions if isinstance(stored.assumptions, dict) else None,
            calculation_hash=stored.calculation_hash,
            analysis_date=stored.created_at,
            indicators_count=stored.indicators_count,
            language=language,
            cost_items=cost_items,
            sensitivity=sensitivity_payload,
            investment_amount=investment,
            horizon_years=horizon,
        )
        return content, filename

    def _to_result(self, stored) -> FinancialAnalysisResult:
        items = stored.indicators.get("items", []) if isinstance(stored.indicators, dict) else []
        indicators = [
            IndicatorResult(
                key=i.get("key", ""),
                label=i.get("label", ""),
                value=i.get("value"),
                unit=i.get("unit", ""),
                category=i.get("category", "geral"),
            )
            for i in items
            if isinstance(i, dict)
        ]
        cf_data = stored.cash_flows if isinstance(stored.cash_flows, dict) else {}
        cash_flows = CashFlowProjection(
            years=cf_data.get("years", []),
            revenue=cf_data.get("revenue", []),
            opex=cf_data.get("opex", []),
            ebitda=cf_data.get("ebitda", []),
            depreciation=cf_data.get("depreciation", []),
            ebit=cf_data.get("ebit", []),
            interest=cf_data.get("interest", []),
            ebt=cf_data.get("ebt", []),
            tax=cf_data.get("tax", []),
            net_income=cf_data.get("net_income", []),
            free_cash_flow=cf_data.get("free_cash_flow", []),
            cumulative_fcf=cf_data.get("cumulative_fcf", []),
        )
        summary = {}
        if isinstance(stored.indicators, dict):
            summary = stored.indicators.get("summary") or {}
        return FinancialAnalysisResult(
            indicators=indicators,
            indicators_by_category=(
                stored.indicators.get("by_category", {})
                if isinstance(stored.indicators, dict)
                else {}
            ),
            cash_flows=cash_flows,
            summary=summary,
        )
