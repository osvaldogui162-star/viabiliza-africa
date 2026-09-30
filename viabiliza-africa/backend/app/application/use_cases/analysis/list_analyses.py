from uuid import UUID

from app.application.services.analysis_access_policy import AnalysisAccessPolicy
from app.application.services.project_context_resolver import ProjectContextResolver
from app.application.use_cases.analysis.mappers import to_analysis_output
from app.domain.exceptions.domain_exceptions import AuthorizationError, EntityNotFoundError
from app.domain.repositories.analysis_repository import IFinancialAnalysisRepository


class ListAnalysesUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        analysis_policy: AnalysisAccessPolicy,
        analysis_repository: IFinancialAnalysisRepository,
    ) -> None:
        self._ctx = context_resolver
        self._policy = analysis_policy
        self._repo = analysis_repository

    def execute(self, *, actor_id: UUID, project_id: UUID, limit: int = 20) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_view_analysis(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão para visualizar análises")

        items = self._repo.find_by_project(project_id, limit=limit)
        return {
            "items": [to_analysis_output(a) for a in items],
            "total": len(items),
        }


class GetAnalysisUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        analysis_policy: AnalysisAccessPolicy,
        analysis_repository: IFinancialAnalysisRepository,
    ) -> None:
        self._ctx = context_resolver
        self._policy = analysis_policy
        self._repo = analysis_repository

    def execute(self, *, actor_id: UUID, project_id: UUID, analysis_id: UUID) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_view_analysis(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão para visualizar análises")

        analysis = self._repo.find_by_id(analysis_id)
        if analysis is None or analysis.project_id != project_id:
            raise EntityNotFoundError("Análise", str(analysis_id))

        return to_analysis_output(analysis)
