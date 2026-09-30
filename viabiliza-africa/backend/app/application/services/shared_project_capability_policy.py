from uuid import UUID

from app.domain.entities.project import Project
from app.domain.entities.project_share import ProjectShare
from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole
from app.domain.repositories.project_share_repository import IProjectShareRepository


class SharedProjectCapabilityPolicy:
    def __init__(self, share_repository: IProjectShareRepository) -> None:
        self._shares = share_repository

    def find_share(self, user_id: UUID, project_id: UUID) -> ProjectShare | None:
        return self._shares.find_by_project_and_user(project_id, user_id)

    def is_owner_or_admin(self, user: User, project: Project) -> bool:
        if not user.is_active:
            return False
        if user.role == UserRole.ADMIN:
            return True
        return project.owner_id == user.id

    def can(self, user: User, project: Project, capability: str) -> bool:
        if self.is_owner_or_admin(user, project):
            return True
        share = self.find_share(user.id, project.id)
        if share is None:
            return False
        return share.allows(capability)
