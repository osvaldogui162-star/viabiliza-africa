"""Gerar e persistir Missão, Visão, Valores, SWOT, riscos e AIPEX."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from app.application.services.project_context_resolver import ProjectContextResolver
from app.application.services.strategic_insights_service import StrategicInsightsService
from app.domain.repositories.project_repository import IProjectRepository


class GenerateStrategicInsightsUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        project_repository: IProjectRepository,
        insights_service: StrategicInsightsService,
    ) -> None:
        self._ctx = context_resolver
        self._projects = project_repository
        self._insights = insights_service

    def execute(self, *, actor_id: UUID, project_id: UUID) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        self._ctx.require_ingest(ctx)

        payload = self._insights.generate(ctx.project)
        generated_at = datetime.now(timezone.utc)

        self._projects.update_strategic_insights(
            project_id,
            mission=payload["mission"],
            vision=payload["vision"],
            core_values=payload["core_values"],
            swot_analysis=payload["swot_analysis"],
            risk_register=payload["risk_register"],
            aipex_incentives=payload["aipex_incentives"],
            strategic_generated_at=generated_at,
        )

        return {
            "project_id": str(project_id),
            "generated_at": generated_at.isoformat(),
            **payload,
        }
