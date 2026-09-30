"""Perfil setorial do projecto — combina módulo, catálogo, benchmarks e estado de implementação."""

from __future__ import annotations

from app.domain.catalog.sector_item_catalog import SectorItemCatalog
from app.domain.catalog.sector_modules import SectorModule, SectorModuleRegistry, SectorUseCase
from app.domain.repositories.analysis_repository import ISectorBenchmarkRepository


class SectorProfileService:
    def __init__(
        self,
        catalog: SectorItemCatalog,
        benchmark_repository: ISectorBenchmarkRepository,
    ) -> None:
        self._catalog = catalog
        self._benchmarks = benchmark_repository

    def build(self, *, sector: str, language: str = "pt") -> dict:
        lang = "en" if language == "en" else "pt"
        primary, esg, related = SectorModuleRegistry.resolve(sector)

        catalog_items = self._catalog.to_preview(sector)
        benchmarks = self._benchmarks.find_by_sector(sector)
        bench_out = [
            {
                "key": b.metric_key,
                "label": b.metric_label,
                "value": float(b.average_value),
                "unit": b.unit,
            }
            for b in benchmarks
        ]

        automated = sum(1 for uc in primary.use_cases if uc.status == "automated")
        partial = sum(1 for uc in primary.use_cases if uc.status == "partial")
        planned = sum(1 for uc in primary.use_cases if uc.status == "planned")

        return {
            "sector": sector,
            "primary_module": self._module_dict(primary, lang),
            "esg_module": self._module_dict(esg, lang, include_all_sectors=True),
            "related_modules": [self._module_dict(m, lang) for m in related],
            "catalog": {
                "items_count": len(catalog_items),
                "items": catalog_items[:30],
                "has_more": len(catalog_items) > 30,
            },
            "benchmarks": bench_out,
            "coverage": {
                "automated": automated,
                "partial": partial,
                "planned": planned,
                "total_use_cases": len(primary.use_cases),
                "catalog_items": len(catalog_items),
                "benchmarks": len(bench_out),
            },
            "business_rules_summary": self._collect_rules(primary, esg, lang),
            "recommended_certifications": list(
                dict.fromkeys(
                    [*primary.certifications, *esg.certifications]
                )
            ),
        }

    def _module_dict(
        self,
        module: SectorModule,
        lang: str,
        *,
        include_all_sectors: bool = False,
    ) -> dict:
        return {
            "code": module.code,
            "name": module.name_en if lang == "en" else module.name_pt,
            "description": module.description_en if lang == "en" else module.description_pt,
            "priority": module.priority,
            "sectors": list(module.sectors) if include_all_sectors or module.sectors else [],
            "kpis": list(module.kpis_en if lang == "en" else module.kpis_pt),
            "certifications": list(module.certifications),
            "use_cases": [self._uc_dict(uc, lang) for uc in module.use_cases],
        }

    def _uc_dict(self, uc: SectorUseCase, lang: str) -> dict:
        return {
            "code": uc.code,
            "title": uc.title_en if lang == "en" else uc.title_pt,
            "status": uc.status,
            "business_rules": list(uc.business_rules),
            "outputs": list(uc.outputs_en if lang == "en" else uc.outputs_pt),
        }

    def _collect_rules(
        self, primary: SectorModule, esg: SectorModule, lang: str
    ) -> list[str]:
        rules: list[str] = []
        for uc in (*primary.use_cases, *esg.use_cases):
            if uc.status in ("automated", "partial"):
                rules.extend(uc.business_rules)
        # dedupe preserving order
        seen: set[str] = set()
        out: list[str] = []
        for r in rules:
            if r not in seen:
                seen.add(r)
                out.append(r)
        return out[:12]
