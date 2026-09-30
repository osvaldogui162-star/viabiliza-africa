from app.domain.entities.financial_analysis import (
    FinancialAnalysis,
    MonteCarloSimulation,
    SensitivityAnalysis,
)


def to_analysis_output(analysis: FinancialAnalysis) -> dict:
    return {
        "id": str(analysis.id),
        "project_id": str(analysis.project_id),
        "assumptions": analysis.assumptions,
        "cash_flows": analysis.cash_flows,
        "indicators": analysis.indicators,
        "indicators_count": analysis.indicators_count,
        "calculation_hash": analysis.calculation_hash,
        "created_by": str(analysis.created_by),
        "created_at": analysis.created_at.isoformat(),
    }


def to_monte_carlo_output(sim: MonteCarloSimulation) -> dict:
    return {
        "id": str(sim.id),
        "project_id": str(sim.project_id),
        "iterations": sim.iterations,
        "parameters": sim.parameters,
        "results": sim.results,
        "analysis_id": str(sim.analysis_id) if sim.analysis_id else None,
        "created_by": str(sim.created_by),
        "created_at": sim.created_at.isoformat(),
    }


def to_sensitivity_output(analysis: SensitivityAnalysis) -> dict:
    return {
        "id": str(analysis.id),
        "project_id": str(analysis.project_id),
        "variables": analysis.variables,
        "results": analysis.results,
        "analysis_id": str(analysis.analysis_id) if analysis.analysis_id else None,
        "created_by": str(analysis.created_by),
        "created_at": analysis.created_at.isoformat(),
    }
