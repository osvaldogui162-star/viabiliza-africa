from app.application.services.project_access_policy import ProjectAccessPolicy
from app.application.services.shared_project_capability_policy import SharedProjectCapabilityPolicy
from app.domain.entities.project import Project
from app.domain.entities.user import User
from app.domain.enums.project_capability import ProjectCapability
from app.domain.enums.user_role import UserRole


class ReportAccessPolicy:
    """Política de acesso para relatórios (Módulo 6)."""

    def __init__(
        self,
        project_policy: ProjectAccessPolicy,
        capability_policy: SharedProjectCapabilityPolicy | None = None,
    ) -> None:
        self._project_policy = project_policy
        self._capabilities = capability_policy

    def can_generate(self, user: User, project: Project, *, is_shared: bool) -> bool:
        """UC28-UC30 — gerar e descarregar."""
        if self._capabilities and not self._capabilities.is_owner_or_admin(user, project):
            return self._capabilities.can(user, project, ProjectCapability.MANAGE_REPORTS.value)
        return self._project_policy.can_view(user, project, is_shared=is_shared)

    def can_download(self, user: User, project: Project, *, is_shared: bool) -> bool:
        return self.can_generate(user, project, is_shared=is_shared)

    def can_print(self, user: User, project: Project, *, is_shared: bool) -> bool:
        """UC33 — impressão."""
        return self.can_generate(user, project, is_shared=is_shared)

    def can_send_email_or_whatsapp(self, user: User, project: Project) -> bool:
        """UC31, UC32 — admin e analista (dono)."""
        if not user.is_active or project.is_deleted:
            return False
        if user.role == UserRole.ADMIN:
            return True
        return user.role == UserRole.FINANCIAL and project.owner_id == user.id

    def can_submit_to_bank(self, user: User, project: Project) -> bool:
        """UC34 — admin e analista (dono)."""
        return self.can_send_email_or_whatsapp(user, project)
