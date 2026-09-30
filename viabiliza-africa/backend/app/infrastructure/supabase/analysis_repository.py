from uuid import UUID

from supabase import Client

from app.domain.entities.financial_analysis import (
    FinancialAnalysis,
    MonteCarloSimulation,
    SectorBenchmark,
    SensitivityAnalysis,
)
from app.domain.repositories.analysis_repository import (
    IFinancialAnalysisRepository,
    IFinancialAssumptionsRepository,
    IMonteCarloRepository,
    ISectorBenchmarkRepository,
    ISensitivityRepository,
)
from app.infrastructure.supabase.analysis_mappers import (
    map_benchmark,
    map_financial_analysis,
    map_monte_carlo,
    map_sensitivity,
)
from app.infrastructure.supabase.response_helpers import get_rows, get_single_row


class SupabaseFinancialAssumptionsRepository(IFinancialAssumptionsRepository):
    TABLE = "financial_assumptions"

    def __init__(self, client: Client) -> None:
        self._client = client

    def find_by_project(self, project_id: UUID) -> dict | None:
        response = (
            self._client.table(self.TABLE)
            .select("assumptions")
            .eq("project_id", str(project_id))
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return row["assumptions"] if row else None

    def upsert(self, project_id: UUID, assumptions: dict, updated_by: UUID) -> dict:
        payload = {
            "project_id": str(project_id),
            "assumptions": assumptions,
            "updated_by": str(updated_by),
        }
        response = (
            self._client.table(self.TABLE)
            .upsert(payload, on_conflict="project_id")
            .execute()
        )
        row = get_single_row(response)
        return row["assumptions"] if row else assumptions


class SupabaseFinancialAnalysisRepository(IFinancialAnalysisRepository):
    TABLE = "financial_analyses"

    def __init__(self, client: Client) -> None:
        self._client = client

    def find_by_id(self, analysis_id: UUID) -> FinancialAnalysis | None:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("id", str(analysis_id))
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return map_financial_analysis(row) if row else None

    def find_by_project(self, project_id: UUID, *, limit: int = 20) -> list[FinancialAnalysis]:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("project_id", str(project_id))
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [map_financial_analysis(r) for r in get_rows(response)]

    def create(
        self,
        *,
        project_id: UUID,
        assumptions: dict,
        cash_flows: dict,
        indicators: dict,
        indicators_count: int,
        calculation_hash: str,
        created_by: UUID,
    ) -> FinancialAnalysis:
        payload = {
            "project_id": str(project_id),
            "assumptions": assumptions,
            "cash_flows": cash_flows,
            "indicators": indicators,
            "indicators_count": indicators_count,
            "calculation_hash": calculation_hash,
            "created_by": str(created_by),
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        row = get_single_row(response)
        return map_financial_analysis(row)


class SupabaseMonteCarloRepository(IMonteCarloRepository):
    TABLE = "monte_carlo_simulations"

    def __init__(self, client: Client) -> None:
        self._client = client

    def find_by_id(self, simulation_id: UUID) -> MonteCarloSimulation | None:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("id", str(simulation_id))
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return map_monte_carlo(row) if row else None

    def find_by_project(self, project_id: UUID, *, limit: int = 10) -> list[MonteCarloSimulation]:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("project_id", str(project_id))
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [map_monte_carlo(r) for r in get_rows(response)]

    def create(
        self,
        *,
        project_id: UUID,
        iterations: int,
        parameters: dict,
        results: dict,
        analysis_id: UUID | None,
        created_by: UUID,
    ) -> MonteCarloSimulation:
        payload = {
            "project_id": str(project_id),
            "iterations": iterations,
            "parameters": parameters,
            "results": results,
            "analysis_id": str(analysis_id) if analysis_id else None,
            "created_by": str(created_by),
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        row = get_single_row(response)
        return map_monte_carlo(row)


class SupabaseSensitivityRepository(ISensitivityRepository):
    TABLE = "sensitivity_analyses"

    def __init__(self, client: Client) -> None:
        self._client = client

    def find_by_id(self, analysis_id: UUID) -> SensitivityAnalysis | None:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("id", str(analysis_id))
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return map_sensitivity(row) if row else None

    def find_by_project(self, project_id: UUID, *, limit: int = 10) -> list[SensitivityAnalysis]:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("project_id", str(project_id))
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [map_sensitivity(r) for r in get_rows(response)]

    def create(
        self,
        *,
        project_id: UUID,
        variables: dict,
        results: dict,
        analysis_id: UUID | None,
        created_by: UUID,
    ) -> SensitivityAnalysis:
        payload = {
            "project_id": str(project_id),
            "variables": variables,
            "results": results,
            "analysis_id": str(analysis_id) if analysis_id else None,
            "created_by": str(created_by),
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        row = get_single_row(response)
        return map_sensitivity(row)


class SupabaseSectorBenchmarkRepository(ISectorBenchmarkRepository):
    TABLE = "sector_benchmarks"

    def __init__(self, client: Client) -> None:
        self._client = client

    def find_by_sector(self, sector: str, *, country: str | None = None) -> list[SectorBenchmark]:
        query = self._client.table(self.TABLE).select("*").eq("sector", sector)
        if country:
            query = query.eq("country", country)
        else:
            query = query.is_("country", "null")
        response = query.execute()
        return [map_benchmark(r) for r in get_rows(response)]
