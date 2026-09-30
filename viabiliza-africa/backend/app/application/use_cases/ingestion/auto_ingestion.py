"""Pipeline de ingestão automática: catálogo → preços reais → orçamento → proforma."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from statistics import median
from uuid import UUID

from app.application.interfaces.hash_service import IHashService
from app.application.interfaces.market_scraper import ScrapedProduct
from app.application.interfaces.qr_code_service import IQRCodeService
from app.application.services.cost_item_hash_builder import CostItemHashBuilder
from app.application.services.project_context_resolver import ProjectContextResolver
from app.application.services.subscription_service import SubscriptionService
from app.application.use_cases.ingestion.mappers import (
    label_for_price_source,
    to_budget_output,
    to_cost_item_output,
    to_proforma_output,
)
from app.config import Config
from app.domain.catalog.angolan_retail_suppliers import (
    ALL_RETAIL_SUPPLIERS,
    GENERAL_MARKETPLACE_CODES,
    resolve_sources_for_item,
)
from app.domain.catalog.sector_item_catalog import CatalogItem, SectorItemCatalog
from app.domain.catalog.sector_modules import SectorModuleRegistry
from app.domain.enums.audit_action import AuditAction
from app.domain.enums.audit_entity_type import AuditEntityType
from app.domain.enums.cost_item_type import CostItemType
from app.domain.enums.data_source import DataSource
from app.domain.enums.scraping_job_status import ScrapingJobStatus
from app.domain.exceptions.domain_exceptions import ValidationError
from app.domain.repositories.audit_trail_repository import IAuditTrailRepository
from app.domain.repositories.budget_repository import IBudgetRepository
from app.domain.repositories.cost_item_repository import ICostItemRepository
from app.domain.repositories.scraping_repository import IScrapingRepository
from app.infrastructure.scraping.scraping_orchestrator import ScrapingOrchestrator


class PreviewAutoIngestionUseCase:
    """Pré-visualiza itens do catálogo setorial sem gravar."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        catalog: SectorItemCatalog,
    ) -> None:
        self._ctx = context_resolver
        self._catalog = catalog

    def execute(self, *, actor_id: UUID, project_id: UUID) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        self._ctx.require_ingest(ctx)
        sector = ctx.project.sector.value
        items = self._catalog.to_preview(sector)
        primary, esg, related = SectorModuleRegistry.resolve(sector)
        retail_names = [s.name for s in ALL_RETAIL_SUPPLIERS[:12]]
        return {
            "sector": sector,
            "project_name": ctx.project.name,
            "currency": ctx.project.currency.value,
            "items": items,
            "total_items": len(items),
            "sector_module": {
                "primary_code": primary.code,
                "primary_name": primary.name_pt,
                "esg_code": esg.code,
                "related_codes": [m.code for m in related],
                "catalog_guidance": (
                    f"Catálogo orientado pelo módulo «{primary.name_pt}» com camada ESG. "
                    f"Inclui itens específicos do sector e referências dos casos de uso UC60–UC100."
                ),
            },
            "sources_hint": [
                *GENERAL_MARKETPLACE_CODES,
                *[s.code for s in ALL_RETAIL_SUPPLIERS if s.scrape_enabled][:20],
            ],
            "retail_suppliers_count": len(ALL_RETAIL_SUPPLIERS),
            "retail_suppliers_sample": retail_names,
        }


class RunAutoIngestionUseCase:
    """
    Ingestão automática completa:
    1) Lista itens necessários do setor
    2) Pesquisa preços em fontes credíveis
    3) Cria cost_items com rastreio da fonte
    4) Gera orçamento + fatura proforma
    5) Devolve documento de transparência (preço + fonte por item)
    """

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        catalog: SectorItemCatalog,
        orchestrator: ScrapingOrchestrator,
        scraping_repository: IScrapingRepository,
        cost_item_repository: ICostItemRepository,
        budget_repository: IBudgetRepository,
        audit_trail_repository: IAuditTrailRepository,
        hash_builder: CostItemHashBuilder,
        hash_service: IHashService,
        qr_service: IQRCodeService,
        config: Config,
        subscription_service: SubscriptionService | None = None,
    ) -> None:
        self._ctx = context_resolver
        self._catalog = catalog
        self._orchestrator = orchestrator
        self._scraping = scraping_repository
        self._items = cost_item_repository
        self._budgets = budget_repository
        self._audit = audit_trail_repository
        self._hash_builder = hash_builder
        self._hash = hash_service
        self._qr = qr_service
        self._config = config
        self._subscription = subscription_service

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        sources: list[str] | None = None,
        replace_existing: bool = False,
        generate_proforma: bool = True,
        item_overrides: list[dict] | None = None,
        ip_address: str | None = None,
    ) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        self._ctx.require_ingest(ctx)

        existing = self._items.find_by_project(project_id)
        if existing and not replace_existing:
            raise ValidationError(
                "O projecto já tem itens de custo. "
                "Confirme replace_existing=true para regenerar a ingestão automática."
            )

        if replace_existing and existing:
            # budget_items.cost_item_id → ON DELETE RESTRICT;
            # proforma.budget_id → ON DELETE RESTRICT — limpar orçamentos primeiro.
            self._budgets.delete_by_project(project_id)
            for item in existing:
                self._items.delete(item.id)

        available = {s["code"] for s in self._scraping.get_active_sources()}
        impl = set(self._orchestrator.available_sources())
        # Scrapers implementados ∩ fontes activas (+ retalho scrapável do domain)
        from app.domain.catalog.angolan_retail_suppliers import scrapable_suppliers

        domain_scrapable = {s.code for s in scrapable_suppliers()} | set(
            GENERAL_MARKETPLACE_CODES
        )
        usable = (available & impl) | (domain_scrapable & impl)
        if not usable:
            usable = impl

        global_selected = None
        if sources:
            global_selected = [s for s in sources if s in impl][:10]

        catalog_items = self._catalog.list_for_sector(ctx.project.sector.value)
        catalog_items = self._apply_item_overrides(catalog_items, item_overrides)
        if not catalog_items:
            raise ValidationError(
                "Nenhum item seleccionado para ingestão. "
                "Indique pelo menos um item com quantidade > 0."
            )

        if self._subscription:
            self._subscription.ensure_auto_ingestion(
                ctx.actor, catalog_items_count=len(catalog_items)
            )

        transparency: list[dict] = []
        created = []
        currency = ctx.project.currency.value
        sources_used: set[str] = set()

        job = self._scraping.create_job(
            project_id=project_id,
            search_query=f"auto-ingestion:{ctx.project.sector.value}",
            sources=global_selected
            or resolve_sources_for_item("Equipamento", available=usable, max_sources=10),
            created_by=actor_id,
        )
        self._scraping.update_job_status(job.id, status=ScrapingJobStatus.RUNNING)

        scrape_payloads: list[dict] = []

        for catalog_item in catalog_items:
            item_sources = global_selected or resolve_sources_for_item(
                catalog_item.category,
                available=usable,
                max_sources=12,
            )
            if not item_sources:
                item_sources = list(GENERAL_MARKETPLACE_CODES)
                item_sources = [s for s in item_sources if s in impl][:4]
            sources_used.update(item_sources)

            try:
                offer = self._resolve_price(
                    catalog_item, item_sources, currency=currency
                )
            except ValidationError as exc:
                transparency.append(
                    {
                        "item_id": None,
                        "description": catalog_item.description,
                        "category": catalog_item.category,
                        "item_type": catalog_item.item_type,
                        "quantity": format(catalog_item.quantity, "f"),
                        "unit": catalog_item.unit,
                        "unit_price": None,
                        "total_amount": None,
                        "currency": currency,
                        "source": "não_encontrado",
                        "source_url": None,
                        "product_name": None,
                        "supplier_name": None,
                        "selection_method": "skipped",
                        "from_marketplace": False,
                        "skip_reason": str(exc),
                    }
                )
                continue

            unit_price = offer["unit_price"]
            source_display = label_for_price_source(
                offer.get("source"),
                supplier_name=offer.get("supplier_name"),
            )
            from app.infrastructure.scraping.supplier_contacts import (
                codes_from_reference_context,
            )

            contact_codes: list[str] = []
            if offer.get("source") == "referencia_sectorial":
                contact_codes = codes_from_reference_context(
                    reference_note=catalog_item.reference_note,
                    category=catalog_item.category,
                    catalog_key=catalog_item.key,
                    description=catalog_item.description,
                )
            elif offer.get("source"):
                contact_codes = [str(offer["source"])]
            for cand in offer.get("candidates") or []:
                src = cand.get("source") if isinstance(cand, dict) else None
                if src and src not in contact_codes:
                    contact_codes.append(str(src))

            meta = {
                "auto_ingestion": True,
                "catalog_key": catalog_item.key,
                "pricing_mode": catalog_item.pricing_mode,
                "search_query": catalog_item.search_query,
                "price_source": offer["source"],
                "price_source_url": offer.get("source_url"),
                "source_display": source_display,
                "supplier_name": offer.get("supplier_name"),
                "product_name": offer.get("product_name"),
                "candidates": offer.get("candidates", []),
                "selection_method": offer.get("selection_method"),
                "reference_note": catalog_item.reference_note,
                "contact_source_codes": contact_codes[:6],
            }

            item_type = CostItemType(catalog_item.item_type)
            data_hash = self._hash_builder.build_hash(
                project_id=project_id,
                item_type=item_type,
                category=catalog_item.category,
                description=catalog_item.description,
                quantity=catalog_item.quantity,
                unit=catalog_item.unit,
                unit_price=unit_price,
                source=DataSource.SCRAPING if offer["from_scrape"] else DataSource.MANUAL,
                supplier_name=offer.get("supplier_name"),
            )

            item = self._items.create(
                project_id=project_id,
                item_type=item_type,
                category=catalog_item.category,
                description=catalog_item.description,
                quantity=catalog_item.quantity,
                unit=catalog_item.unit,
                unit_price=unit_price,
                currency=ctx.project.currency,
                source=DataSource.SCRAPING if offer["from_scrape"] else DataSource.MANUAL,
                data_hash=data_hash,
                supplier_name=offer.get("supplier_name"),
                supplier_nif=None,
                supplier_url=offer.get("source_url"),
                scraping_result_id=None,
                metadata=meta,
                created_by=actor_id,
            )
            created.append(item)

            line = {
                "item_id": str(item.id),
                "description": catalog_item.description,
                "category": catalog_item.category,
                "item_type": catalog_item.item_type,
                "quantity": format(catalog_item.quantity, "f"),
                "unit": catalog_item.unit,
                "unit_price": format(unit_price, "f"),
                "total_amount": format(item.total_amount, "f"),
                "currency": currency,
                "source": offer["source"],
                "source_url": offer.get("source_url"),
                "product_name": offer.get("product_name"),
                "supplier_name": offer.get("supplier_name"),
                "selection_method": offer.get("selection_method"),
                "from_marketplace": offer["from_scrape"],
            }
            transparency.append(line)

            if offer.get("raw_products"):
                for product in offer["raw_products"][:5]:
                    scrape_payloads.append(
                        {
                            "job_id": str(job.id),
                            "project_id": str(project_id),
                            "source": product.source,
                            "supplier_name": product.supplier_name,
                            "product_name": f"[{catalog_item.key}] {product.product_name}",
                            "price": str(product.price),
                            "currency": product.currency,
                            "product_url": product.product_url,
                            "data_hash": self._hash.hash_dict(
                                {
                                    "catalog": catalog_item.key,
                                    "source": product.source,
                                    "product": product.product_name,
                                    "price": str(product.price),
                                }
                            ),
                        }
                    )

        if scrape_payloads:
            self._scraping.create_results(scrape_payloads)
        self._scraping.update_job_status(
            job.id,
            status=ScrapingJobStatus.COMPLETED,
            results_count=len(scrape_payloads),
        )

        if not created:
            raise ValidationError(
                "Nenhum item com preço encontrado nas fontes consultadas. "
                "Tente novamente ou adicione itens manualmente."
            )

        # Orçamento rastreável
        item_hashes = [i.data_hash for i in created]
        verification_hash = self._hash.hash_chain(*item_hashes)
        budget_number = self._budgets.next_budget_number()
        total = sum(i.total_amount for i in created)
        verify_url = f"{self._config.FRONTEND_BASE_URL}/verify/budget/{verification_hash}"
        qr = self._qr.generate(verify_url)
        budget_items_payload = [
            {
                "cost_item_id": str(item.id),
                "item_type": item.item_type.value,
                "category": item.category,
                "description": item.description,
                "quantity": str(item.quantity),
                "unit": item.unit,
                "unit_price": str(item.unit_price),
                "total_amount": str(item.total_amount),
                "item_hash": item.data_hash,
                "supplier_name": item.supplier_name,
                "line_order": index,
            }
            for index, item in enumerate(created)
        ]
        budget = self._budgets.create_budget(
            project_id=project_id,
            budget_number=budget_number,
            title=f"Orçamento automático — {ctx.project.name}",
            total_amount=total,
            currency=currency,
            verification_hash=verification_hash,
            qr_code_data=qr.data,
            qr_code_image=qr.image_base64,
            created_by=actor_id,
            items=budget_items_payload,
        )

        self._audit.create(
            project_id=project_id,
            entity_type=AuditEntityType.BUDGET,
            entity_id=budget.id,
            action=AuditAction.BUDGET_GENERATED,
            actor_id=actor_id,
            data_hash=verification_hash,
            ip_address=ip_address,
            metadata={
                "auto_ingestion": True,
                "budget_number": budget_number,
                "items": len(created),
                "sources": sorted(sources_used),
            },
        )

        proforma_out = None
        if generate_proforma:
            invoice_number = self._budgets.next_invoice_number()
            proforma_hash = self._hash.hash_dict(
                {
                    "budget_hash": verification_hash,
                    "client": ctx.project.company_name,
                    "invoice": invoice_number,
                }
            )
            verify_url = (
                f"{self._config.FRONTEND_BASE_URL}/verify/budget/{verification_hash}"
            )
            qr = self._qr.generate(verify_url)
            invoice = self._budgets.create_proforma(
                budget_id=budget.id,
                project_id=project_id,
                invoice_number=invoice_number,
                client_name=ctx.project.company_name,
                client_tax_id=ctx.project.company_tax_id,
                total_amount=budget.total_amount,
                currency=budget.currency,
                verification_hash=proforma_hash,
                notes=(
                    "Fatura proforma gerada pela ingestão automática. "
                    "Cada linha tem fonte de preço documentada no relatório de transparência."
                ),
                created_by=actor_id,
                qr_code_data=qr.data,
                qr_code_image=qr.image_base64,
            )
            self._audit.create(
                project_id=project_id,
                entity_type=AuditEntityType.PROFORMA,
                entity_id=invoice.id,
                action=AuditAction.PROFORMA_GENERATED,
                actor_id=actor_id,
                data_hash=proforma_hash,
                ip_address=ip_address,
                metadata={"auto_ingestion": True, "invoice_number": invoice_number},
            )
            proforma_out = to_proforma_output(invoice)

        transparency_doc = {
            "title": "Documento de transparência de preços",
            "project_id": str(project_id),
            "project_name": ctx.project.name,
            "sector": ctx.project.sector.value,
            "company_name": ctx.project.company_name,
            "company_tax_id": ctx.project.company_tax_id,
            "currency": currency,
            "sources_consulted": sorted(sources_used),
            "methodology": (
                "Para bens materiais, o sistema consulta marketplaces angolanos "
                "(Jumia, Jiji, Kikolo, Socia, Praça Digital) e retalhistas locais "
                "por categoria (supermercados, construção, eléctrico, IT, móveis, "
                "auto, farmácias, eletrodomésticos, papelarias, agricultura, EPI). "
                "Selecciona o preço mediano entre ofertas válidas. Para serviços e "
                "mão-de-obra, combina pesquisa com referências setoriais quando o "
                "marketplace não devolve preço."
            ),
            "lines": transparency,
            "totals": {
                "capex": format(
                    sum(
                        i.total_amount
                        for i in created
                        if i.item_type == CostItemType.CAPEX
                    ),
                    "f",
                ),
                "opex": format(
                    sum(
                        i.total_amount
                        for i in created
                        if i.item_type == CostItemType.OPEX
                    ),
                    "f",
                ),
                "grand_total": format(total, "f"),
            },
            "verification_hash": verification_hash,
            "verify_url": verify_url,
            "next_steps": [
                "Rever o documento de transparência (preço + fonte por item)",
                "Aprovar o orçamento se estiver conforme",
                "Calcular demonstrações / indicadores na tab Análise",
                "Gerar o relatório final do projecto",
            ],
        }

        return {
            "items": [to_cost_item_output(i) for i in created],
            "items_count": len(created),
            "budget": to_budget_output(budget, items_count=len(created)),
            "proforma": proforma_out,
            "transparency_document": transparency_doc,
            "scraping_job_id": str(job.id),
            "sources_used": sorted(sources_used),
        }

    @staticmethod
    def _apply_item_overrides(
        catalog_items: list[CatalogItem],
        item_overrides: list[dict] | None,
    ) -> list[CatalogItem]:
        """Aplica seleção e quantidades enviadas pelo modal de ingestão."""
        if not item_overrides:
            return catalog_items

        by_key = {row.get("key"): row for row in item_overrides if row.get("key")}
        if not by_key:
            return catalog_items

        selected: list[CatalogItem] = []
        for item in catalog_items:
            ov = by_key.get(item.key)
            if ov is None:
                continue
            if ov.get("include") is False:
                continue
            qty_raw = ov.get("quantity", item.quantity)
            qty = Decimal(str(qty_raw))
            if qty <= 0:
                continue
            selected.append(replace(item, quantity=qty))
        return selected

    def _resolve_price(
        self,
        catalog_item: CatalogItem,
        sources: list[str],
        *,
        currency: str,
    ) -> dict:
        products: list[ScrapedProduct] = []
        # reference puro: não bloqueia em scrapers lentos
        if catalog_item.pricing_mode == "reference" and catalog_item.reference_price is not None:
            return {
                "unit_price": catalog_item.reference_price.quantize(Decimal("0.01")),
                "source": "referencia_sectorial",
                "source_url": None,
                "supplier_name": "Referência setorial AO",
                "product_name": catalog_item.description,
                "selection_method": "sector_reference",
                "from_scrape": False,
                "candidates": [],
                "raw_products": [],
                "reference_note": catalog_item.reference_note,
            }

        if catalog_item.pricing_mode in ("scrape", "hybrid"):
            products = self._orchestrator.search(
                catalog_item.search_query,
                sources,
                currency=currency,
                stop_after=6,
                include_slow_remote=True,
                use_market_board=True,
            )

        # Garantir fallback directo à tabela de mercado se a onda ficou vazia
        if not products:
            from app.domain.catalog.angolan_market_price_board import lookup_market_board

            products = lookup_market_board(
                catalog_item.search_query, currency=currency
            )

        candidates = [
            {
                "source": p.source,
                "product_name": p.product_name,
                "supplier_name": p.supplier_name,
                "price": format(p.price, "f"),
                "url": p.product_url,
            }
            for p in products[:12]
        ]

        if products:
            prices = sorted(p.price for p in products)
            chosen_price = median(prices)
            best = min(products, key=lambda p: abs(p.price - chosen_price))
            # Ofertas da tabela de mercado AO (lojas reais) vs scrape HTML
            from app.domain.catalog.angolan_market_price_board import lookup_market_board

            board_codes = {p.source for p in lookup_market_board(catalog_item.search_query)}
            method = (
                "angolan_market_board"
                if best.source in board_codes and len(products) <= len(board_codes) + 1
                else "median_closest_offer"
            )
            return {
                "unit_price": Decimal(best.price).quantize(Decimal("0.01")),
                "source": best.source,
                "source_url": best.product_url,
                "supplier_name": best.supplier_name,
                "product_name": best.product_name,
                "selection_method": method,
                "from_scrape": True,
                "candidates": candidates,
                "raw_products": products,
            }

        if catalog_item.reference_price is not None:
            return {
                "unit_price": catalog_item.reference_price.quantize(Decimal("0.01")),
                "source": "referencia_sectorial",
                "source_url": None,
                "supplier_name": "Referência setorial AO",
                "product_name": catalog_item.description,
                "selection_method": "sector_reference",
                "from_scrape": False,
                "candidates": candidates,
                "raw_products": [],
                "reference_note": catalog_item.reference_note,
            }

        raise ValidationError(
            f"Sem preço encontrado para «{catalog_item.description}» "
            f"(pesquisa: {catalog_item.search_query})."
        )
