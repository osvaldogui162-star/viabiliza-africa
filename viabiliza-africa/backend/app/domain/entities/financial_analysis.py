from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class FinancialAnalysis:
    id: UUID
    project_id: UUID
    assumptions: dict
    cash_flows: dict
    indicators: dict
    indicators_count: int
    calculation_hash: str
    created_by: UUID
    created_at: datetime


@dataclass
class MonteCarloSimulation:
    id: UUID
    project_id: UUID
    iterations: int
    parameters: dict
    results: dict
    analysis_id: UUID | None
    created_by: UUID
    created_at: datetime


@dataclass
class SensitivityAnalysis:
    id: UUID
    project_id: UUID
    variables: dict
    results: dict
    analysis_id: UUID | None
    created_by: UUID
    created_at: datetime


@dataclass
class SectorBenchmark:
    id: UUID
    sector: str
    country: str | None
    metric_key: str
    metric_label: str
    average_value: float
    unit: str
    source: str
