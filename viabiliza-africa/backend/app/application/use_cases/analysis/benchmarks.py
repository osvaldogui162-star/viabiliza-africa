from uuid import UUID

from app.application.services.analysis_access_policy import AnalysisAccessPolicy
from app.application.services.project_context_resolver import ProjectContextResolver
from app.domain.exceptions.domain_exceptions import AuthorizationError
from app.domain.repositories.analysis_repository import (
    IFinancialAnalysisRepository,
    ISectorBenchmarkRepository,
)


class CompareBenchmarksUseCase:
    """UC22 — Comparar indicadores com benchmarks do setor africano."""

    METRIC_MAP = {
        "irr": "tir",
        "roi": "roi",
        "npv_margin": "npv_investment_ratio",
        "payback_years": "payback_simple",
        "ebitda_margin": "ebitda_margin",
    }

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        analysis_policy: AnalysisAccessPolicy,
        benchmark_repository: ISectorBenchmarkRepository,
        analysis_repository: IFinancialAnalysisRepository,
    ) -> None:
        self._ctx = context_resolver
        self._policy = analysis_policy
        self._benchmarks = benchmark_repository
        self._analysis = analysis_repository

    def execute(self, *, actor_id: UUID, project_id: UUID) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_view_benchmarks(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão para visualizar benchmarks")

        sector = ctx.project.sector.value
        benchmarks = self._benchmarks.find_by_sector(sector)

        analyses = self._analysis.find_by_project(project_id, limit=1)
        project_metrics: dict[str, float | None] = {}
        if analyses:
            summary = analyses[0].indicators.get("summary", {})
            items = {
                i["key"]: i["value"]
                for i in analyses[0].indicators.get("items", [])
            }
            project_metrics = {**items, **summary}

        comparisons = []
        for bench in benchmarks:
            indicator_key = self.METRIC_MAP.get(bench.metric_key, bench.metric_key)
            project_value = project_metrics.get(indicator_key)
            diff = None
            status = "no_data"
            if project_value is not None:
                diff = round(float(project_value) - bench.average_value, 4)
                if diff > 0:
                    status = "above"
                elif diff < 0:
                    status = "below"
                else:
                    status = "equal"

            comparisons.append(
                {
                    "metric_key": bench.metric_key,
                    "metric_label": bench.metric_label,
                    "indicator_key": indicator_key,
                    "benchmark_value": bench.average_value,
                    "project_value": project_value,
                    "difference": diff,
                    "unit": bench.unit,
                    "status": status,
                    "source": bench.source,
                }
            )

        return {
            "sector": sector,
            "country": ctx.project.country.value,
            "has_analysis": bool(analyses),
            "comparisons": comparisons,
            "total": len(comparisons),
        }
