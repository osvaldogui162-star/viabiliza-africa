from app.application.services.project_access_policy import ProjectAccessPolicy
from app.application.services.shared_project_capability_policy import SharedProjectCapabilityPolicy
from app.domain.entities.project import Project
from app.domain.entities.user import User
from app.domain.enums.project_capability import ProjectCapability
from app.domain.enums.user_role import UserRole


class IngestionAccessPolicy:
    """Política de acesso para ingestão de dados (Módulo 3)."""

    def __init__(
        self,
        project_policy: ProjectAccessPolicy,
        capability_policy: SharedProjectCapabilityPolicy | None = None,
    ) -> None:
        self._project_policy = project_policy
        self._capabilities = capability_policy

    def can_ingest(self, user: User, project: Project) -> bool:
        """UC12-UC17: importar, scraping, orçamento."""
        if not user.is_active or project.is_deleted:
            return False
        if self._capabilities:
            return (
                self._capabilities.can(user, project, ProjectCapability.MANAGE_INGESTION.value)
                or self._capabilities.can(user, project, ProjectCapability.MANAGE_COSTS.value)
            )
        if user.role == UserRole.ADMIN:
            return True
        return user.role == UserRole.FINANCIAL and project.owner_id == user.id

    def can_view_audit_trail(
        self, user: User, project: Project, *, is_shared: bool
    ) -> bool:
        """UC18: admin (todos), analista (os seus). Utilizador comum: sem acesso."""
        if not user.is_active or project.is_deleted:
            return False
        if user.role == UserRole.ADMIN:
            return True
        if user.role == UserRole.FINANCIAL and project.owner_id == user.id:
            return True
        return False

    def can_view_ingestion_data(
        self, user: User, project: Project, *, is_shared: bool
    ) -> bool:
        """Visualizar itens/orçamentos — quem tem acesso ao projeto."""
        return self._project_policy.can_view(user, project, is_shared=is_shared)
