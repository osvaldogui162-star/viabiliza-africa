from app.application.services.project_access_policy import ProjectAccessPolicy
from app.application.services.shared_project_capability_policy import SharedProjectCapabilityPolicy
from app.domain.entities.project import Project
from app.domain.entities.user import User
from app.domain.enums.project_capability import ProjectCapability


class AnalysisAccessPolicy:
    """Política de acesso para análise financeira (Módulo 4)."""

    def __init__(
        self,
        project_policy: ProjectAccessPolicy,
        capability_policy: SharedProjectCapabilityPolicy | None = None,
    ) -> None:
        self._project_policy = project_policy
        self._capabilities = capability_policy

    def can_execute_analysis(self, user: User, project: Project) -> bool:
        """UC19-UC21, UC23 — calcular, simular, exportar."""
        if not user.is_active or project.is_deleted:
            return False
        if self._capabilities:
            return self._capabilities.can(user, project, ProjectCapability.RUN_ANALYSIS.value)
        return self._project_policy.can_edit(user, project)

    def can_view_analysis(self, user: User, project: Project, *, is_shared: bool) -> bool:
        """Visualizar resultados de análise — quem tem acesso ao projeto."""
        return self._project_policy.can_view(user, project, is_shared=is_shared)

    def can_view_benchmarks(self, user: User, project: Project, *, is_shared: bool) -> bool:
        """UC22 — benchmarks: admin, analista e utilizador com acesso ao projeto."""
        return self._project_policy.can_view(user, project, is_shared=is_shared)
