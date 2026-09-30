from uuid import UUID

from app.application.dto.project_dto import ListProjectsInput
from app.application.services.project_access_policy import ProjectAccessPolicy
from app.application.use_cases.projects.project_mapper import to_project_output
from app.domain.entities.project import Project
from app.domain.enums.country import Country
from app.domain.enums.project_sector import ProjectSector
from app.domain.enums.project_status import ProjectStatus
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, ValidationError
from app.domain.repositories.project_repository import IProjectRepository, ProjectFilters
from app.domain.repositories.project_share_repository import IProjectShareRepository
from app.domain.repositories.user_repository import IUserRepository


class ListProjectsUseCase:
    """UC07 — Listar projetos com filtros."""

    def __init__(
        self,
        user_repository: IUserRepository,
        project_repository: IProjectRepository,
        project_share_repository: IProjectShareRepository,
        access_policy: ProjectAccessPolicy,
    ) -> None:
        self._users = user_repository
        self._projects = project_repository
        self._shares = project_share_repository
        self._policy = access_policy

    def execute(self, input_data: ListProjectsInput) -> dict:
        actor = self._users.find_by_id(input_data.actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(input_data.actor_id))

        status = self._parse_status(input_data.status)
        country = Country(input_data.country.upper()) if input_data.country else None
        sector = ProjectSector(input_data.sector) if input_data.sector else None

        scope = self._policy.resolve_list_scope(actor)
        filters = ProjectFilters(
            status=status,
            country=country,
            sector=sector,
            search=input_data.search,
        )

        if scope == "shared":
            shared_ids = self._shares.find_project_ids_for_user(actor.id)
            if not shared_ids:
                return {
                    "items": [],
                    "total": 0,
                    "limit": input_data.limit,
                    "offset": input_data.offset,
                }
            return self._list_by_ids(
                actor.id, shared_ids, filters, input_data.limit, input_data.offset
            )

        if scope == "owned_and_shared":
            return self._list_owned_and_shared(
                actor.id, filters, input_data.limit, input_data.offset
            )

        if scope == "owned":
            filters.owner_id = actor.id

        projects = self._projects.find_all(
            filters, limit=input_data.limit, offset=input_data.offset
        )
        total = self._projects.count(filters)
        items = self._build_items(projects, actor.id)

        return {
            "items": items,
            "total": total,
            "limit": input_data.limit,
            "offset": input_data.offset,
        }

    def _list_owned_and_shared(
        self,
        actor_id: UUID,
        filters: ProjectFilters,
        limit: int,
        offset: int,
    ) -> dict:
        owned_filters = ProjectFilters(
            status=filters.status,
            country=filters.country,
            sector=filters.sector,
            search=filters.search,
            owner_id=actor_id,
        )
        owned_keys = self._projects.find_id_timestamps(owned_filters)
        owned_id_set = {key[0] for key in owned_keys}

        shared_ids = self._shares.find_project_ids_for_user(actor_id)
        extra_shared = [pid for pid in shared_ids if pid not in owned_id_set]
        shared_keys = (
            self._projects.find_id_timestamps(filters, only_ids=extra_shared)
            if extra_shared
            else []
        )

        merged = owned_keys + shared_keys
        merged.sort(key=lambda pair: pair[1], reverse=True)
        total = len(merged)
        page_keys = merged[offset : offset + limit]
        page_ids = [key[0] for key in page_keys]
        ordered = self._projects_ordered(page_ids)
        return {
            "items": self._build_items(ordered, actor_id),
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def _list_by_ids(
        self,
        actor_id: UUID,
        project_ids: list[UUID],
        filters: ProjectFilters,
        limit: int,
        offset: int,
    ) -> dict:
        keys = self._projects.find_id_timestamps(filters, only_ids=project_ids)
        keys.sort(key=lambda pair: pair[1], reverse=True)
        total = len(keys)
        page_keys = keys[offset : offset + limit]
        page_ids = [key[0] for key in page_keys]
        ordered = self._projects_ordered(page_ids)
        return {
            "items": self._build_items(ordered, actor_id),
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def _projects_ordered(self, project_ids: list[UUID]) -> list[Project]:
        if not project_ids:
            return []
        loaded = self._projects.find_by_ids(project_ids)
        by_id = {project.id: project for project in loaded}
        return [by_id[pid] for pid in project_ids if pid in by_id]

    def _build_items(self, projects: list[Project], actor_id: UUID) -> list[dict]:
        if not projects:
            return []

        project_ids = [p.id for p in projects]
        owner_ids = list({p.owner_id for p in projects})

        owners = self._users.find_by_ids(owner_ids)
        shared_ids = self._shares.find_shared_project_ids(actor_id, project_ids)
        shares_counts: dict = {}
        if len(project_ids) <= 50:
            shares_counts = self._shares.count_by_projects(project_ids)

        items = []
        for project in projects:
            items.append(
                to_project_output(
                    project,
                    owner=owners.get(project.owner_id),
                    actor_id=actor_id,
                    is_shared=project.owner_id != actor_id and project.id in shared_ids,
                    shares_count=shares_counts.get(project.id, 0),
                )
            )
        return items

    def _parse_status(self, status: str | None) -> ProjectStatus | None:
        if not status:
            return None
        if not ProjectStatus.is_valid(status):
            raise ValidationError(
                f"Status inválido. Valores: {', '.join(ProjectStatus.values())}"
            )
        return ProjectStatus(status)
