from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.financial_analysis import (
    FinancialAnalysis,
    MonteCarloSimulation,
    SensitivityAnalysis,
    SectorBenchmark,
)


class IFinancialAssumptionsRepository(ABC):
    @abstractmethod
    def find_by_project(self, project_id: UUID) -> dict | None:
        ...

    @abstractmethod
    def upsert(self, project_id: UUID, assumptions: dict, updated_by: UUID) -> dict:
        ...


class IFinancialAnalysisRepository(ABC):
    @abstractmethod
    def find_by_id(self, analysis_id: UUID) -> FinancialAnalysis | None:
        ...

    @abstractmethod
    def find_by_project(self, project_id: UUID, *, limit: int = 20) -> list[FinancialAnalysis]:
        ...

    @abstractmethod
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
        ...


class IMonteCarloRepository(ABC):
    @abstractmethod
    def find_by_id(self, simulation_id: UUID) -> MonteCarloSimulation | None:
        ...

    @abstractmethod
    def find_by_project(self, project_id: UUID, *, limit: int = 10) -> list[MonteCarloSimulation]:
        ...

    @abstractmethod
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
        ...


class ISensitivityRepository(ABC):
    @abstractmethod
    def find_by_id(self, analysis_id: UUID) -> SensitivityAnalysis | None:
        ...

    @abstractmethod
    def find_by_project(self, project_id: UUID, *, limit: int = 10) -> list[SensitivityAnalysis]:
        ...

    @abstractmethod
    def create(
        self,
        *,
        project_id: UUID,
        variables: dict,
        results: dict,
        analysis_id: UUID | None,
        created_by: UUID,
    ) -> SensitivityAnalysis:
        ...


class ISectorBenchmarkRepository(ABC):
    @abstractmethod
    def find_by_sector(self, sector: str, *, country: str | None = None) -> list[SectorBenchmark]:
        ...
