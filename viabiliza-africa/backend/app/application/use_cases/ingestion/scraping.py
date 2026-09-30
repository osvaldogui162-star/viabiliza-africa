from decimal import Decimal
from uuid import UUID

from app.application.interfaces.hash_service import IHashService
from app.application.services.project_context_resolver import ProjectContextResolver
from app.application.use_cases.ingestion.mappers import (
    to_scraping_job_output,
    to_scraping_result_output,
    to_scraping_source_output,
)
from app.domain.enums.audit_action import AuditAction
from app.domain.enums.audit_entity_type import AuditEntityType
from app.domain.enums.cost_item_type import CostItemType
from app.domain.enums.data_source import DataSource
from app.domain.enums.scraping_job_status import ScrapingJobStatus
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, ValidationError
from app.domain.repositories.audit_trail_repository import IAuditTrailRepository
from app.domain.repositories.cost_item_repository import ICostItemRepository
from app.domain.repositories.scraping_repository import IScrapingRepository
from app.application.services.cost_item_hash_builder import CostItemHashBuilder
from app.application.services.subscription_service import SubscriptionService
from app.infrastructure.scraping.scraping_orchestrator import ScrapingOrchestrator


class ExecuteScrapingUseCase:
    """UC14 — Executar scraping automático."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        scraping_repository: IScrapingRepository,
        audit_trail_repository: IAuditTrailRepository,
        orchestrator: ScrapingOrchestrator,
        hash_service: IHashService,
        subscription_service: SubscriptionService,
    ) -> None:
        self._ctx = context_resolver
        self._scraping = scraping_repository
        self._audit = audit_trail_repository
        self._orchestrator = orchestrator
        self._hash = hash_service
        self._subscription = subscription_service

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        search_query: str,
        sources: list[str] | None = None,
        ip_address: str | None = None,
    ):
        ctx = self._ctx.resolve(actor_id, project_id)
        self._ctx.require_ingest(ctx)
        self._subscription.ensure_scraping(ctx.actor, items_to_add=10)

        if not search_query.strip():
            raise ValidationError("Termo de pesquisa é obrigatório")

        available = {s["code"] for s in self._scraping.get_active_sources()}
        impl = set(self._orchestrator.available_sources())

        from app.domain.catalog.angolan_retail_suppliers import (
            resolve_sources_for_item,
            scrapable_suppliers,
        )

        if sources:
            selected = [s for s in sources if s in impl]
            invalid = [s for s in sources if s not in available and s not in impl]
            if invalid and not selected:
                raise ValidationError(f"Fontes inválidas: {', '.join(invalid)}")
        else:
            # Por defeito: lojas locais scrapáveis + marketplaces (evita só Jumia/Jiji)
            preferred = resolve_sources_for_item(
                "Equipamento",
                available=impl | available,
                max_sources=14,
            )
            extras = [s.code for s in scrapable_suppliers() if s.code in impl]
            selected = []
            for code in preferred + extras:
                if code in impl and code not in selected:
                    selected.append(code)
            selected = selected[:14] or list(impl)[:10]

        if not selected:
            raise ValidationError("Nenhuma fonte de scraping disponível")

        job = self._scraping.create_job(
            project_id=project_id,
            search_query=search_query.strip(),
            sources=selected,
            created_by=actor_id,
        )
        self._scraping.update_job_status(job.id, status=ScrapingJobStatus.RUNNING)

        try:
            products = self._orchestrator.search(
                search_query,
                selected,
                currency=ctx.project.currency.value,
                stop_after=10,
                include_slow_remote=True,
                use_market_board=True,
            )
            result_payloads = []
            for product in products:
                data_hash = self._hash.hash_dict(
                    {
                        "source": product.source,
                        "product": product.product_name,
                        "price": str(product.price),
                        "query": search_query,
                    }
                )
                result_payloads.append(
                    {
                        "job_id": str(job.id),
                        "project_id": str(project_id),
                        "source": product.source,
                        "supplier_name": product.supplier_name,
                        "product_name": product.product_name,
                        "price": str(product.price),
                        "currency": product.currency,
                        "product_url": product.product_url,
                        "data_hash": data_hash,
                    }
                )
            results = self._scraping.create_results(result_payloads)
            job = self._scraping.update_job_status(
                job.id,
                status=ScrapingJobStatus.COMPLETED,
                results_count=len(results),
            )
            audit_hash = self._hash.hash_chain(*[r.data_hash for r in results]) if results else self._hash.hash_string(job.id.hex)
            self._audit.create(
                project_id=project_id,
                entity_type=AuditEntityType.SCRAPING_JOB,
                entity_id=job.id,
                action=AuditAction.SCRAPING_COMPLETED,
                actor_id=actor_id,
                data_hash=audit_hash,
                ip_address=ip_address,
                metadata={"query": search_query, "results": len(results)},
            )
            return {
                "job": to_scraping_job_output(job),
                "results": [to_scraping_result_output(r) for r in results],
            }
        except Exception as exc:
            self._scraping.update_job_status(
                job.id, status=ScrapingJobStatus.FAILED, error_message=str(exc)
            )
            raise


class SelectSupplierUseCase:
    """UC15 — Selecionar fornecedor e criar item de custo."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        scraping_repository: IScrapingRepository,
        cost_item_repository: ICostItemRepository,
        audit_trail_repository: IAuditTrailRepository,
        hash_builder: CostItemHashBuilder,
    ) -> None:
        self._ctx = context_resolver
        self._scraping = scraping_repository
        self._items = cost_item_repository
        self._audit = audit_trail_repository
        self._hash_builder = hash_builder

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        result_id: UUID,
        item_type: str = "capex",
        category: str = "Equipamento",
        quantity: Decimal = Decimal("1"),
        ip_address: str | None = None,
    ):
        ctx = self._ctx.resolve(actor_id, project_id)
        self._ctx.require_ingest(ctx)

        result = self._scraping.find_result_by_id(result_id)
        if result is None or result.project_id != project_id:
            raise EntityNotFoundError("Resultado de scraping", str(result_id))

        item_type_enum = CostItemType(item_type)
        description = result.product_name
        data_hash = self._hash_builder.build_hash(
            project_id=project_id,
            item_type=item_type_enum,
            category=category,
            description=description,
            quantity=quantity,
            unit="un",
            unit_price=result.price,
            source=DataSource.SCRAPING,
            supplier_name=result.supplier_name,
        )

        item = self._items.create(
            project_id=project_id,
            item_type=item_type_enum,
            category=category,
            description=description,
            quantity=quantity,
            unit="un",
            unit_price=result.price,
            currency=ctx.project.currency,
            source=DataSource.SCRAPING,
            data_hash=data_hash,
            supplier_name=result.supplier_name,
            supplier_nif=None,
            supplier_url=result.product_url,
            scraping_result_id=result.id,
            metadata={"scraping_source": result.source, "source_display": result.supplier_name or result.source, "price_source": result.source},
            created_by=actor_id,
        )

        self._scraping.select_result(result_id, cost_item_id=item.id)
        self._audit.create(
            project_id=project_id,
            entity_type=AuditEntityType.SCRAPING_RESULT,
            entity_id=result_id,
            action=AuditAction.SUPPLIER_SELECTED,
            actor_id=actor_id,
            data_hash=data_hash,
            ip_address=ip_address,
            metadata={"cost_item_id": str(item.id), "supplier": result.supplier_name},
        )
        from app.application.use_cases.ingestion.mappers import to_cost_item_output as _out

        return _out(item)


class GetScrapingJobUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        scraping_repository: IScrapingRepository,
    ) -> None:
        self._ctx = context_resolver
        self._scraping = scraping_repository

    def execute(self, *, actor_id: UUID, project_id: UUID, job_id: UUID) -> dict:
        self._ctx.resolve(actor_id, project_id)
        job = self._scraping.find_job_by_id(job_id)
        if job is None or job.project_id != project_id:
            raise EntityNotFoundError("Job de scraping", str(job_id))
        results = self._scraping.find_results_by_job(job_id)
        return {
            "job": to_scraping_job_output(job),
            "results": [to_scraping_result_output(r) for r in results],
        }


class ListScrapingSourcesUseCase:
    def __init__(self, scraping_repository: IScrapingRepository) -> None:
        self._scraping = scraping_repository

    def execute(self) -> dict:
        sources = self._scraping.get_active_sources()
        return {
            "items": [to_scraping_source_output(s) for s in sources],
            "total": len(sources),
        }
