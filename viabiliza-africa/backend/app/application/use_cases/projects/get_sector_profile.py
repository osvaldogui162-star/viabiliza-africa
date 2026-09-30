from uuid import UUID

from app.application.services.project_context_resolver import ProjectContextResolver
from app.application.services.sector_profile_service import SectorProfileService


class GetSectorProfileUseCase:
    """Perfil setorial do projecto (módulo, UCs, catálogo, benchmarks)."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        sector_profile_service: SectorProfileService,
    ) -> None:
        self._ctx = context_resolver
        self._profiles = sector_profile_service

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        language: str | None = None,
    ) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        lang = language or "pt"
        profile = self._profiles.build(sector=ctx.project.sector.value, language=lang)
        profile["project_id"] = str(project_id)
        profile["project_name"] = ctx.project.name
        return profile
