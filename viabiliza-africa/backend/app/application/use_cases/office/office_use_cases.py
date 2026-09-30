from uuid import UUID

from app.application.services.project_access_policy import ProjectAccessPolicy
from app.application.services.shared_project_capability_policy import SharedProjectCapabilityPolicy
from app.application.use_cases.projects.project_mapper import to_share_output
from app.application.use_cases.projects.share_project import ShareProjectUseCase
from app.domain.enums.project_capability import ProjectCapability
from app.domain.enums.share_permission import SharePermission
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.domain_exceptions import (
    AuthorizationError,
    ConflictError,
    EntityNotFoundError,
    ValidationError,
)
from app.domain.repositories.analyst_office_repository import IAnalystOfficeRepository
from app.domain.repositories.project_repository import IProjectRepository, ProjectFilters
from app.domain.repositories.project_share_repository import IProjectShareRepository
from app.domain.repositories.user_repository import IUserRepository
from app.domain.services.share_capabilities import capability_labels_pt, merge_capabilities


class OfficeAccessPolicy:
    def resolve_owner_id(self, actor, requested_owner_id: UUID | None) -> UUID:
        if actor.role == UserRole.ADMIN:
            if requested_owner_id is None:
                raise ValidationError("Indique o analista (owner_id) para consulta administrativa.")
            return requested_owner_id
        if actor.role != UserRole.FINANCIAL:
            raise AuthorizationError("Apenas analistas gerem o escritório.")
        return actor.id

    def can_manage_office(self, actor, owner_id: UUID) -> bool:
        if not actor.is_active:
            return False
        if actor.role == UserRole.ADMIN:
            return True
        return actor.role == UserRole.FINANCIAL and actor.id == owner_id


def _member_output(member, *, project_ids: list[str] | None = None) -> dict:
    return {
        "id": str(member.id),
        "owner_id": str(member.owner_id),
        "user_id": str(member.user_id) if member.user_id else None,
        "email": member.email,
        "full_name": member.full_name,
        "job_title": member.job_title,
        "status": member.status,
        "notes": member.notes,
        "project_ids": project_ids or [],
        "created_at": member.created_at.isoformat(),
        "updated_at": member.updated_at.isoformat(),
    }


class GetOfficeDashboardUseCase:
    def __init__(
        self,
        users: IUserRepository,
        projects: IProjectRepository,
        shares: IProjectShareRepository,
        office: IAnalystOfficeRepository,
        policy: OfficeAccessPolicy,
    ) -> None:
        self._users = users
        self._projects = projects
        self._shares = shares
        self._office = office
        self._policy = policy

    def execute(self, *, actor_id: UUID, owner_id: UUID | None = None) -> dict:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))
        resolved_owner = self._policy.resolve_owner_id(actor, owner_id)
        if not self._policy.can_manage_office(actor, resolved_owner):
            raise AuthorizationError("Sem acesso")

        owner = self._users.find_by_id(resolved_owner)
        project_rows = self._projects.find_all(
            ProjectFilters(owner_id=resolved_owner), limit=200, offset=0
        )
        project_ids = [p.id for p in project_rows]
        share_counts = self._shares.count_by_projects(project_ids)
        members = self._office.find_by_owner(resolved_owner)

        return {
            "owner": {
                "id": str(resolved_owner),
                "full_name": owner.full_name if owner else "",
                "email": owner.email if owner else "",
            },
            "stats": {
                "projects_count": len(project_rows),
                "members_count": len(members),
                "shared_slots": sum(share_counts.values()),
            },
            "capability_catalog": [
                {"key": k, "label_pt": capability_labels_pt()[k]}
                for k in ProjectCapability.keys()
            ],
            "projects": [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "company_name": p.company_name,
                    "status": p.status.value,
                    "shares_count": share_counts.get(p.id, 0),
                }
                for p in project_rows
            ],
        }


class ListOfficeMembersUseCase:
    def __init__(
        self,
        users: IUserRepository,
        office: IAnalystOfficeRepository,
        shares: IProjectShareRepository,
        policy: OfficeAccessPolicy,
    ) -> None:
        self._users = users
        self._office = office
        self._shares = shares
        self._policy = policy

    def execute(self, *, actor_id: UUID, owner_id: UUID | None = None) -> dict:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))
        resolved_owner = self._policy.resolve_owner_id(actor, owner_id)
        if not self._policy.can_manage_office(actor, resolved_owner):
            raise AuthorizationError("Sem acesso")

        members = self._office.find_by_owner(resolved_owner)
        member_ids = [m.id for m in members]
        projects_by_member = self._shares.project_ids_by_office_members(member_ids)
        items = []
        for member in members:
            project_ids = [str(pid) for pid in projects_by_member.get(member.id, [])]
            items.append(_member_output(member, project_ids=project_ids))
        return {"items": items, "total": len(items)}


class CreateOfficeMemberUseCase:
    def __init__(
        self,
        users: IUserRepository,
        office: IAnalystOfficeRepository,
        policy: OfficeAccessPolicy,
    ) -> None:
        self._users = users
        self._office = office
        self._policy = policy

    def execute(
        self,
        *,
        actor_id: UUID,
        owner_id: UUID | None,
        email: str,
        full_name: str,
        job_title: str,
        notes: str | None = None,
    ) -> dict:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))
        resolved_owner = self._policy.resolve_owner_id(actor, owner_id)
        if not self._policy.can_manage_office(actor, resolved_owner):
            raise AuthorizationError("Sem acesso")

        normalized_email = email.strip().lower()
        if not normalized_email or "@" not in normalized_email:
            raise ValidationError("Email inválido")
        if self._office.find_by_owner_and_email(resolved_owner, normalized_email):
            raise ConflictError("Já existe um profissional activo com este email no escritório.")

        linked_user = self._users.find_by_email(normalized_email)
        if linked_user and linked_user.role == UserRole.ADMIN:
            raise ValidationError("Não é possível adicionar administradores ao escritório.")

        created = self._office.create(
            owner_id=resolved_owner,
            email=normalized_email,
            full_name=full_name,
            job_title=job_title,
            user_id=linked_user.id if linked_user else None,
            notes=notes,
        )
        return _member_output(created)


class UpdateOfficeMemberUseCase:
    def __init__(
        self,
        users: IUserRepository,
        office: IAnalystOfficeRepository,
        policy: OfficeAccessPolicy,
    ) -> None:
        self._users = users
        self._office = office
        self._policy = policy

    def execute(
        self,
        *,
        actor_id: UUID,
        member_id: UUID,
        full_name: str | None = None,
        job_title: str | None = None,
        notes: str | None = None,
    ) -> dict:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))
        member = self._office.find_by_id(member_id)
        if member is None:
            raise EntityNotFoundError("Profissional", str(member_id))
        if not self._policy.can_manage_office(actor, member.owner_id):
            raise AuthorizationError("Sem acesso")

        updated = self._office.update(
            member_id,
            full_name=full_name,
            job_title=job_title,
            notes=notes,
        )
        return _member_output(updated)


class ArchiveOfficeMemberUseCase:
    def __init__(
        self,
        users: IUserRepository,
        office: IAnalystOfficeRepository,
        policy: OfficeAccessPolicy,
    ) -> None:
        self._users = users
        self._office = office
        self._policy = policy

    def execute(self, *, actor_id: UUID, member_id: UUID) -> dict:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))
        member = self._office.find_by_id(member_id)
        if member is None:
            raise EntityNotFoundError("Profissional", str(member_id))
        if not self._policy.can_manage_office(actor, member.owner_id):
            raise AuthorizationError("Sem acesso")
        updated = self._office.update(member_id, status="archived")
        return _member_output(updated)


class AssignOfficeMemberProjectsUseCase:
    def __init__(
        self,
        users: IUserRepository,
        projects: IProjectRepository,
        office: IAnalystOfficeRepository,
        shares: IProjectShareRepository,
        policy: OfficeAccessPolicy,
        project_policy: ProjectAccessPolicy,
        share_project: ShareProjectUseCase,
    ) -> None:
        self._users = users
        self._projects = projects
        self._office = office
        self._shares = shares
        self._policy = policy
        self._project_policy = project_policy
        self._share_project = share_project

    def execute(
        self,
        *,
        actor_id: UUID,
        member_id: UUID,
        project_ids: list[UUID] | None = None,
        permission: str = "collaborate",
        capabilities: dict[str, bool] | None = None,
        assignments: list[dict] | None = None,
    ) -> dict:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))
        member = self._office.find_by_id(member_id)
        if member is None or not member.is_active:
            raise EntityNotFoundError("Profissional", str(member_id))
        if not self._policy.can_manage_office(actor, member.owner_id):
            raise AuthorizationError("Sem acesso")
        work_items: list[dict] = []
        if assignments:
            for row in assignments:
                pid = row.get("project_id")
                if pid is None:
                    raise ValidationError("project_id em falta na atribuição.")
                perm_str = row.get("permission") or permission
                if not SharePermission.is_valid(perm_str):
                    raise ValidationError("Permissão inválida")
                work_items.append(
                    {
                        "project_id": UUID(str(pid)) if not isinstance(pid, UUID) else pid,
                        "permission": SharePermission(perm_str),
                        "capabilities": merge_capabilities(
                            SharePermission(perm_str),
                            row.get("capabilities"),
                        ),
                    }
                )
        elif project_ids:
            if not SharePermission.is_valid(permission):
                raise ValidationError("Permissão inválida")
            perm = SharePermission(permission)
            merged_caps = merge_capabilities(perm, capabilities)
            work_items = [
                {"project_id": pid, "permission": perm, "capabilities": merged_caps}
                for pid in project_ids
            ]
        else:
            raise ValidationError("Seleccione pelo menos um projecto.")

        if not work_items:
            raise ValidationError("Seleccione pelo menos um projecto.")

        results: list[dict] = []
        for item in work_items:
            pid = item["project_id"]
            perm = item["permission"]
            merged_caps = item["capabilities"]
            project = self._projects.find_by_id(pid)
            if project is None or project.owner_id != member.owner_id:
                raise ValidationError(f"Projecto inválido ou não pertence ao analista: {pid}")

            if member.user_id is None:
                from app.application.dto.project_dto import ShareProjectInput

                invite_result = self._share_project.execute(
                    ShareProjectInput(
                        actor_id=actor_id,
                        project_id=pid,
                        user_email=member.email,
                        permission=perm.value,
                        capabilities=merged_caps,
                        office_member_id=member.id,
                        job_title=member.job_title,
                    )
                )
                pending = getattr(invite_result, "pending_invite", False)
                results.append(
                    {
                        "project_id": str(pid),
                        "status": "invite_pending" if pending else "shared",
                        "message": getattr(invite_result, "message", None),
                    }
                )
                continue

            existing = self._shares.find_by_project_and_user(pid, member.user_id)
            if existing:
                share = self._shares.update(
                    pid,
                    member.user_id,
                    permission=perm,
                    office_member_id=member.id,
                    job_title=member.job_title,
                    capabilities=merged_caps,
                )
            else:
                share = self._shares.create(
                    project_id=pid,
                    user_id=member.user_id,
                    shared_by=actor_id,
                    permission=perm,
                    office_member_id=member.id,
                    job_title=member.job_title,
                    capabilities=merged_caps,
                )
            user = self._users.find_by_id(member.user_id)
            shared_by = self._users.find_by_id(share.shared_by)
            if user and shared_by:
                results.append(
                    {
                        "project_id": str(pid),
                        "status": "shared",
                        "share": to_share_output(share, user=user, shared_by_user=shared_by),
                    }
                )

        return {"results": results, "member_id": str(member_id)}


class ListOfficeMemberAccessUseCase:
    def __init__(
        self,
        users: IUserRepository,
        projects: IProjectRepository,
        office: IAnalystOfficeRepository,
        shares: IProjectShareRepository,
        policy: OfficeAccessPolicy,
    ) -> None:
        self._users = users
        self._projects = projects
        self._office = office
        self._shares = shares
        self._policy = policy

    def execute(self, *, actor_id: UUID, member_id: UUID) -> dict:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))
        member = self._office.find_by_id(member_id)
        if member is None:
            raise EntityNotFoundError("Profissional", str(member_id))
        if not self._policy.can_manage_office(actor, member.owner_id):
            raise AuthorizationError("Sem acesso")

        items: list[dict] = []
        for share in self._shares.find_by_office_member(member.id):
            project = self._projects.find_by_id(share.project_id)
            if project is None:
                continue
            items.append(
                {
                    "project_id": str(share.project_id),
                    "project_name": project.name,
                    "permission": share.permission.value,
                    "job_title": share.job_title,
                    "capabilities": share.capabilities,
                    "effective_capabilities": share.effective_capabilities(),
                }
            )
        if member.user_id:
            owned = self._projects.find_all(
                ProjectFilters(owner_id=member.owner_id), limit=200, offset=0
            )
            seen = {i["project_id"] for i in items}
            for project in owned:
                share = self._shares.find_by_project_and_user(project.id, member.user_id)
                if share is None or str(project.id) in seen:
                    continue
                items.append(
                    {
                        "project_id": str(share.project_id),
                        "project_name": project.name,
                        "permission": share.permission.value,
                        "job_title": share.job_title,
                        "capabilities": share.capabilities,
                        "effective_capabilities": share.effective_capabilities(),
                    }
                )
        return {"member_id": str(member_id), "items": items, "total": len(items)}


class AdminListOfficesUseCase:
    def __init__(
        self,
        users: IUserRepository,
        office: IAnalystOfficeRepository,
        projects: IProjectRepository,
    ) -> None:
        self._users = users
        self._office = office
        self._projects = projects

    def execute(self, *, actor_id: UUID) -> dict:
        actor = self._users.find_by_id(actor_id)
        if actor is None or actor.role != UserRole.ADMIN:
            raise AuthorizationError("Apenas administradores")

        summaries = self._office.list_all_summaries(limit=500)
        items = []
        seen_owners: set[str] = set()
        for row in summaries:
            oid = UUID(row["owner_id"])
            seen_owners.add(row["owner_id"])
            owner = self._users.find_by_id(oid)
            if owner is None or owner.role != UserRole.FINANCIAL:
                continue
            owned = self._projects.find_all(ProjectFilters(owner_id=oid), limit=500, offset=0)
            items.append(
                {
                    "owner_id": row["owner_id"],
                    "owner_name": owner.full_name,
                    "owner_email": owner.email,
                    "active_members": row["active_members"],
                    "projects_count": len(owned),
                }
            )

        financials = self._users.find_all(role=UserRole.FINANCIAL, limit=300, offset=0)
        for fin in financials:
            if str(fin.id) in seen_owners:
                continue
            owned = self._projects.find_all(ProjectFilters(owner_id=fin.id), limit=500, offset=0)
            items.append(
                {
                    "owner_id": str(fin.id),
                    "owner_name": fin.full_name,
                    "owner_email": fin.email,
                    "active_members": self._office.count_by_owner(fin.id),
                    "projects_count": len(owned),
                }
            )

        items.sort(key=lambda x: x["owner_name"].lower())
        return {"items": items, "total": len(items)}
