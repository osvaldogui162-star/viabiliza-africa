from enum import Enum


class ProjectCapability(str, Enum):
    VIEW_PROJECT = "view_project"
    EDIT_PROJECT = "edit_project"
    MANAGE_COSTS = "manage_costs"
    RUN_ANALYSIS = "run_analysis"
    MANAGE_REPORTS = "manage_reports"
    MANAGE_COLLABORATION = "manage_collaboration"
    MANAGE_INGESTION = "manage_ingestion"
    VIEW_FINANCING = "view_financing"

    @classmethod
    def keys(cls) -> list[str]:
        return [c.value for c in cls]
