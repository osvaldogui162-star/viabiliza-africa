from datetime import datetime
from uuid import UUID

from app.domain.entities.financial_analysis import (
    FinancialAnalysis,
    MonteCarloSimulation,
    SectorBenchmark,
    SensitivityAnalysis,
)


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def map_financial_analysis(row: dict) -> FinancialAnalysis:
    return FinancialAnalysis(
        id=UUID(row["id"]),
        project_id=UUID(row["project_id"]),
        assumptions=row["assumptions"],
        cash_flows=row["cash_flows"],
        indicators=row["indicators"],
        indicators_count=row["indicators_count"],
        calculation_hash=row["calculation_hash"],
        created_by=UUID(row["created_by"]),
        created_at=_parse_dt(row["created_at"]),
    )


def map_monte_carlo(row: dict) -> MonteCarloSimulation:
    return MonteCarloSimulation(
        id=UUID(row["id"]),
        project_id=UUID(row["project_id"]),
        iterations=row["iterations"],
        parameters=row["parameters"],
        results=row["results"],
        analysis_id=UUID(row["analysis_id"]) if row.get("analysis_id") else None,
        created_by=UUID(row["created_by"]),
        created_at=_parse_dt(row["created_at"]),
    )


def map_sensitivity(row: dict) -> SensitivityAnalysis:
    return SensitivityAnalysis(
        id=UUID(row["id"]),
        project_id=UUID(row["project_id"]),
        variables=row["variables"],
        results=row["results"],
        analysis_id=UUID(row["analysis_id"]) if row.get("analysis_id") else None,
        created_by=UUID(row["created_by"]),
        created_at=_parse_dt(row["created_at"]),
    )


def map_benchmark(row: dict) -> SectorBenchmark:
    return SectorBenchmark(
        id=UUID(row["id"]),
        sector=row["sector"],
        country=row.get("country"),
        metric_key=row["metric_key"],
        metric_label=row["metric_label"],
        average_value=float(row["average_value"]),
        unit=row["unit"],
        source=row.get("source", "Média setorial africana"),
    )
