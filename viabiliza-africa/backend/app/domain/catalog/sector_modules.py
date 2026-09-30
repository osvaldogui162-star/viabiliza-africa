"""Módulos setoriais avançados — especificação ViabilizA+ v5.0 (UC60–UC100).

Cada projecto é enquadrado num módulo primário conforme o sector económico,
com camada ESG transversal e integrações cross-sector quando aplicável.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.domain.enums.project_sector import ProjectSector

Priority = Literal["high", "medium", "low", "esg", "cross"]
UseCaseStatus = Literal["automated", "partial", "planned"]


@dataclass(frozen=True)
class SectorUseCase:
    code: str
    title_pt: str
    title_en: str
    business_rules: tuple[str, ...]
    status: UseCaseStatus
    outputs_pt: tuple[str, ...]
    outputs_en: tuple[str, ...]


@dataclass(frozen=True)
class SectorModule:
    code: str
    name_pt: str
    name_en: str
    description_pt: str
    description_en: str
    priority: Priority
    sectors: tuple[str, ...]
    use_cases: tuple[SectorUseCase, ...]
    kpis_pt: tuple[str, ...]
    kpis_en: tuple[str, ...]
    certifications: tuple[str, ...]


def _uc(
    code: str,
    title_pt: str,
    title_en: str,
    rules: tuple[str, ...],
    status: UseCaseStatus,
    out_pt: tuple[str, ...],
    out_en: tuple[str, ...],
) -> SectorUseCase:
    return SectorUseCase(code, title_pt, title_en, rules, status, out_pt, out_en)


# ── Módulo 1: Agricultura Inteligente ────────────────────────────────────────

_AGRI = SectorModule(
    code="agri_tech",
    name_pt="Agricultura Inteligente (AgriTech)",
    name_en="Smart Agriculture (AgriTech)",
    description_pt=(
        "Projectos agrícolas com IoT, análise de solo, modelos de cultura, irrigação "
        "e viabilidade económica por safra."
    ),
    description_en=(
        "Agricultural projects with IoT, soil analysis, crop models, irrigation "
        "and per-harvest economic viability."
    ),
    priority="high",
    sectors=(ProjectSector.AGRICULTURE.value,),
    use_cases=(
        _uc("UC60", "Gestão de Sensores IoT no Campo", "Field IoT Sensor Management",
            ("RN89: Dados com timestamp preciso", "RN90: Alertas fora do intervalo"), "planned",
            ("Dashboard em tempo real", "Alertas de anomalias"),
            ("Real-time dashboard", "Anomaly alerts")),
        _uc("UC61", "Análise Automática de Solo", "Automated Soil Analysis",
            ("RN91: Referência por cultura", "RN92: Padrões FAO/Embrapa"), "partial",
            ("Interpretação do solo", "Custo de correção/ha"),
            ("Soil interpretation", "Correction cost/ha")),
        _uc("UC62", "Modelação de Culturas (DSSAT)", "Crop Modelling (DSSAT)",
            ("RN93: ≥ 42 culturas", "RN94: API de clima"), "planned",
            ("Produção esperada ton/ha", "Calendário agrícola"),
            ("Expected yield ton/ha", "Crop calendar")),
        _uc("UC63", "Irrigação Inteligente", "Smart Irrigation",
            ("RN95: Dados Sentinel-2", "RN96: Recomendação em tempo real"), "partial",
            ("Recomendação de irrigação", "Economia de água"),
            ("Irrigation recommendation", "Water savings")),
        _uc("UC64", "Deteção de Doenças e Pragas", "Disease & Pest Detection",
            ("RN97: ≥ 20 doenças", "RN98: Base FAO"), "planned",
            ("Diagnóstico", "Custo de tratamento"),
            ("Diagnosis", "Treatment cost")),
        _uc("UC65", "Análise Económica por Safra", "Per-Harvest Economic Analysis",
            ("RN99: Payback em safras", "RN100: Inclui custeio"), "partial",
            ("Margem por safra", "Break-even"),
            ("Margin per harvest", "Break-even")),
        _uc("UC66", "Adequação de Terras (Suitability)", "Land Suitability Assessment",
            ("RN101: Metodologia FAO", "RN102: Classificação S1–S3–N"), "planned",
            ("Mapa de adequação", "Produção potencial"),
            ("Suitability map", "Potential yield")),
        _uc("UC67", "Gestão de Fertilizantes", "Fertiliser Management",
            ("RN103: Recomendações agronómicas", "RN104: Ajuste por fase"), "partial",
            ("Formulação NPK", "Custo/ha"),
            ("NPK formulation", "Cost/ha")),
        _uc("UC68", "Avisos Climáticos e Pragas (iSAT)", "Climate & Pest Advisories (iSAT)",
            ("RN105: Integração iSAT", "RN106: Avisos SMS/WhatsApp"), "planned",
            ("Avisos 5 dias", "Alertas de pragas"),
            ("5-day advisories", "Pest alerts")),
    ),
    kpis_pt=("Produção (ton/ha)", "Custo/ha", "Margem por safra", "Payback (safras)", "Uso hídrico"),
    kpis_en=("Yield (ton/ha)", "Cost/ha", "Margin per harvest", "Payback (harvests)", "Water use"),
    certifications=("GlobalGAP", "Orgânico UE", "ISO 22000"),
)

# ── Módulo 2: Indústria 4.0 ──────────────────────────────────────────────────

_INDUSTRY = SectorModule(
    code="industry_40",
    name_pt="Indústria 4.0 (Manufatura)",
    name_en="Industry 4.0 (Manufacturing)",
    description_pt="Capacidade produtiva, custo unitário, make-or-buy, manutenção e ESG industrial.",
    description_en="Production capacity, unit cost, make-or-buy, maintenance and industrial ESG.",
    priority="high",
    sectors=(ProjectSector.MANUFACTURING.value, ProjectSector.MINING.value),
    use_cases=(
        _uc("UC69", "Dimensionamento de Fábrica", "Factory Sizing & Capacity",
            ("RN107: Capacidade = alvo / (dias × horas × eficiência)",), "partial",
            ("CAPEX estimado", "Área necessária"),
            ("Estimated CAPEX", "Required area")),
        _uc("UC70", "Simulação de Processo (Digital Twin)", "Process Simulation (Digital Twin)",
            ("RN108: Discrete Event Simulation", "RN109: Integração IoT"), "planned",
            ("Gargalos", "Eficiência"),
            ("Bottlenecks", "Efficiency")),
        _uc("UC71", "Manutenção Preditiva", "Predictive Maintenance",
            ("RN110: MTBF/MTTR", "RN111: Custo de paragem"), "planned",
            ("Plano de manutenção", "Custo estimado"),
            ("Maintenance plan", "Estimated cost")),
        _uc("UC72", "Custo Unitário de Produção", "Unit Production Cost",
            ("RN112: CU = (CV + CF) / produção",), "partial",
            ("Custo unitário", "Margem de contribuição"),
            ("Unit cost", "Contribution margin")),
        _uc("UC73", "Make or Buy", "Make or Buy Analysis",
            ("RN113: Custos ocultos", "RN114: Capacidade"), "partial",
            ("Recomendação", "Economia estimada"),
            ("Recommendation", "Estimated savings")),
        _uc("UC74", "Análise de Ociosidade", "Idle Capacity Analysis",
            ("RN115: Ociosidade = 1 - prod/capacidade", "RN116: Cenários automáticos"), "partial",
            ("Taxa de ociosidade", "Impacto financeiro"),
            ("Idle rate", "Financial impact")),
        _uc("UC75", "Gestão de Fornecedores", "Supplier Management",
            ("RN117: Stock segurança = consumo × lead time × fator",), "partial",
            ("Matriz de fornecedores", "Stock de segurança"),
            ("Supplier matrix", "Safety stock")),
        _uc("UC76", "Sustentabilidade Industrial (ESG)", "Industrial Sustainability (ESG)",
            ("RN118: ISO 14000", "RN119: Benchmarks setoriais"), "partial",
            ("Pegada de carbono", "Intensidade energética"),
            ("Carbon footprint", "Energy intensity")),
    ),
    kpis_pt=("OEE", "Custo unitário", "Capacidade utilizada", "Margem bruta", "MTBF"),
    kpis_en=("OEE", "Unit cost", "Capacity utilisation", "Gross margin", "MTBF"),
    certifications=("ISO 9001", "ISO 14001", "ISO 45001"),
)

# ── Módulo 3: Infraestruturas ─────────────────────────────────────────────────

_INFRA = SectorModule(
    code="infrastructure",
    name_pt="Infraestruturas (Energy & Utilities)",
    name_en="Infrastructure (Energy & Utilities)",
    description_pt="Energia solar, hídrica, água/saneamento, estradas e telecomunicações.",
    description_en="Solar, hydro, water/sanitation, roads and telecommunications.",
    priority="medium",
    sectors=(
        ProjectSector.ENERGY.value,
        ProjectSector.CONSTRUCTION.value,
        ProjectSector.REAL_ESTATE.value,
        ProjectSector.TECHNOLOGY.value,
    ),
    use_cases=(
        _uc("UC77", "Viabilidade Solar (FV)", "Solar PV Feasibility",
            ("RN120: PVGIS", "RN121: LCOE = (CAPEX+OPEX)/produção"), "partial",
            ("Produção kWh", "LCOE", "Payback"),
            ("kWh output", "LCOE", "Payback")),
        _uc("UC78", "Viabilidade Hídrica", "Hydro Feasibility",
            ("RN122: Metodologia barragens", "RN123: Impacto ambiental"), "planned",
            ("Potência MW", "CAPEX/OPEX"),
            ("MW capacity", "CAPEX/OPEX")),
        _uc("UC79", "Redes de Água e Saneamento", "Water & Sanitation Networks",
            ("RN124: Perdas 20–40%", "RN125: Tarifa = OPEX+amort/consumo"), "planned",
            ("Dimensionamento", "Tarifa"),
            ("Sizing", "Tariff")),
        _uc("UC80", "Viabilidade de Estradas", "Road Feasibility",
            ("RN126: Custo/km benchmark", "RN127: Manutenção incluída"), "partial",
            ("Custo construção", "VPL/TIR"),
            ("Construction cost", "NPV/IRR")),
        _uc("UC81", "Gestão de Ativos de Infraestrutura", "Infrastructure Asset Management",
            ("RN128: Depreciação linear", "RN129: Manutenção 1–3% CAPEX/ano"), "partial",
            ("Depreciação", "CAPEX futuro"),
            ("Depreciation", "Future CAPEX")),
        _uc("UC82", "Torres de Telecomunicações", "Telecom Tower Feasibility",
            ("RN130: Propagação", "RN131: Custo energia"), "planned",
            ("Nº torres", "Receitas aluguer"),
            ("Tower count", "Lease revenue")),
    ),
    kpis_pt=("LCOE", "Produção anual", "Payback", "CAPEX/km", "Taxa de perdas"),
    kpis_en=("LCOE", "Annual output", "Payback", "CAPEX/km", "Loss rate"),
    certifications=("ISO 50001", "LEED", "ISO 14001"),
)

# ── Módulo 4: Mobilidade ─────────────────────────────────────────────────────

_MOBILITY = SectorModule(
    code="mobility",
    name_pt="Mobilidade Urbana & Logística",
    name_en="Urban Mobility & Logistics",
    description_pt="Frotas, ride-hailing, logística, terminais e segurança social de motoristas.",
    description_en="Fleets, ride-hailing, logistics, terminals and driver social security.",
    priority="medium",
    sectors=(ProjectSector.TRANSPORT.value,),
    use_cases=(
        _uc("UC83", "Viabilidade de Frota", "Fleet Feasibility",
            ("RN132: Combustível, manutenção, seguros",), "partial",
            ("Frota necessária", "CAPEX/OPEX"),
            ("Fleet size", "CAPEX/OPEX")),
        _uc("UC84", "Expansão de Motoristas (Ride-Hailing)", "Driver Expansion Model",
            ("RN133: CAC", "RN134: LTV"), "planned",
            ("Projeção motoristas", "Rentabilidade"),
            ("Driver projection", "Profitability")),
        _uc("UC85", "Logística e Cadeia de Suprimentos", "Logistics & Supply Chain",
            ("RN135: Custo = distância × tarifa × volume",), "partial",
            ("Custo logístico", "Rotas optimizadas"),
            ("Logistics cost", "Optimised routes")),
        _uc("UC86", "Segurança Social de Motoristas", "Driver Social Security",
            ("RN136: Legislação angolana", "RN137: Seguro acidentes"), "planned",
            ("Custo total", "Sustentabilidade social"),
            ("Total cost", "Social sustainability")),
        _uc("UC87", "Terminais e Centros de Distribuição", "Terminals & Distribution Centres",
            ("RN138: Padrões de terminais", "RN139: Equipamentos"), "partial",
            ("Área necessária", "Viabilidade"),
            ("Required area", "Feasibility")),
    ),
    kpis_pt=("Custo/km", "Ocupação frota", "Lead time", "CAC", "LTV"),
    kpis_en=("Cost/km", "Fleet utilisation", "Lead time", "CAC", "LTV"),
    certifications=("ISO 39001",),
)

# ── Módulo 5: Turismo ────────────────────────────────────────────────────────

_TOURISM = SectorModule(
    code="tourism",
    name_pt="Turismo & Hotelaria",
    name_en="Tourism & Hospitality",
    description_pt="Hotelaria, parques, eco-turismo, eventos e turismo comunitário.",
    description_en="Hotels, theme parks, eco-tourism, events and community tourism.",
    priority="low",
    sectors=(ProjectSector.TOURISM.value,),
    use_cases=(
        _uc("UC88", "Viabilidade Hoteleira", "Hotel Feasibility",
            ("RN140: Ocupação 50–70%", "RN141: Sazonalidade"), "partial",
            ("CAPEX/OPEX", "VPL/TIR/Payback"),
            ("CAPEX/OPEX", "NPV/IRR/Payback")),
        _uc("UC89", "Parques Temáticos", "Theme Parks",
            ("RN142: Sazonalidade", "RN143: Benchmarks"), "planned",
            ("Visitantes", "Receitas"),
            ("Visitors", "Revenue")),
        _uc("UC90", "Eco-Turismo", "Eco-Tourism",
            ("RN144: Certificações eco",), "partial",
            ("Impacto ESG", "Receitas"),
            ("ESG impact", "Revenue")),
        _uc("UC91", "Turismo de Negócios", "Business Tourism",
            ("RN145: Ocupação centros eventos",), "planned",
            ("Eventos/ano", "Receitas"),
            ("Events/year", "Revenue")),
        _uc("UC92", "Turismo Comunitário", "Community Tourism",
            ("RN146: Modelos comunitários",), "planned",
            ("Benefícios locais", "Impacto social"),
            ("Local benefits", "Social impact")),
    ),
    kpis_pt=("Taxa de ocupação", "RevPAR", "ADR", "Payback", "Sazonalidade"),
    kpis_en=("Occupancy rate", "RevPAR", "ADR", "Payback", "Seasonality"),
    certifications=("GSTC", "Green Key", "ISO 21401"),
)

# ── Módulo 6: ESG (transversal) ──────────────────────────────────────────────

_ESG = SectorModule(
    code="esg",
    name_pt="ESG & Sustentabilidade",
    name_en="ESG & Sustainability",
    description_pt="Camada transversal: carbono, SROI, governança e certificações para todos os sectores.",
    description_en="Cross-cutting layer: carbon, SROI, governance and certifications for all sectors.",
    priority="esg",
    sectors=tuple(s.value for s in ProjectSector),
    use_cases=(
        _uc("UC93", "Pegada de Carbono Setorial", "Sectoral Carbon Footprint",
            ("RN147: Fatores IPCC", "RN148: Benchmarks por sector"), "partial",
            ("tCO2e", "Intensidade emissões"),
            ("tCO2e", "Emission intensity")),
        _uc("UC94", "Impacto Social (SROI)", "Social Impact (SROI)",
            ("RN149: SROI = benefícios/investimento × 100",), "planned",
            ("SROI", "Empregos criados"),
            ("SROI", "Jobs created")),
        _uc("UC95", "Governança e Compliance", "Governance & Compliance",
            ("RN150: Padrões OCDE",), "partial",
            ("Score governança", "Recomendações"),
            ("Governance score", "Recommendations")),
        _uc("UC96", "Relatório ESG Integrado", "Integrated ESG Report",
            ("RN151: GRI Standards", "RN152: Incluir no relatório final"), "partial",
            ("Relatório ESG",),
            ("ESG report",)),
        _uc("UC97", "Certificações ESG", "ESG Certifications",
            ("RN153: ISO, LEED, etc.",), "partial",
            ("Certificações", "Plano e custo"),
            ("Certifications", "Plan and cost")),
    ),
    kpis_pt=("tCO2e", "SROI", "Empregos directos", "Score ESG"),
    kpis_en=("tCO2e", "SROI", "Direct jobs", "ESG score"),
    certifications=("GRI", "ISO 14001", "ISO 26000", "LEED"),
)

# ── Módulo 7: Cross-Sector ───────────────────────────────────────────────────

_CROSS = SectorModule(
    code="cross_sector",
    name_pt="Cross-Sector (Integração)",
    name_en="Cross-Sector (Integration)",
    description_pt="Integração entre módulos para projectos multidisciplinares (agroindústria, irrigação+agricultura).",
    description_en="Integration across modules for multidisciplinary projects.",
    priority="cross",
    sectors=(),
    use_cases=(
        _uc("UC98", "Agroindústria", "Agro-Industry Integration",
            ("RN154: Integrar módulos", "RN155: Optimização margem"), "planned",
            ("Cadeia de valor", "Sinergias"),
            ("Value chain", "Synergies")),
        _uc("UC99", "Infraestrutura + Agricultura", "Infrastructure + Agriculture",
            ("RN156: Modelos irrigação",), "planned",
            ("Eficiência hídrica", "Viabilidade conjunta"),
            ("Water efficiency", "Joint feasibility")),
        _uc("UC100", "Dashboard Multi-Setorial", "Multi-Sector Dashboard",
            ("RN157: Integração total", "RN158: Tempo real"), "planned",
            ("Indicadores consolidados",),
            ("Consolidated indicators",)),
    ),
    kpis_pt=("Sinergias", "Margem integrada", "Custo logístico"),
    kpis_en=("Synergies", "Integrated margin", "Logistics cost"),
    certifications=(),
)

_ALL_MODULES: dict[str, SectorModule] = {
    m.code: m for m in (_AGRI, _INDUSTRY, _INFRA, _MOBILITY, _TOURISM, _ESG, _CROSS)
}

# Sector económico → módulo primário (demais usam serviços gerais)
_PRIMARY_MODULE_BY_SECTOR: dict[str, str] = {
    ProjectSector.AGRICULTURE.value: "agri_tech",
    ProjectSector.MANUFACTURING.value: "industry_40",
    ProjectSector.MINING.value: "industry_40",
    ProjectSector.ENERGY.value: "infrastructure",
    ProjectSector.CONSTRUCTION.value: "infrastructure",
    ProjectSector.REAL_ESTATE.value: "infrastructure",
    ProjectSector.TECHNOLOGY.value: "infrastructure",
    ProjectSector.TRANSPORT.value: "mobility",
    ProjectSector.TOURISM.value: "tourism",
    ProjectSector.SERVICES.value: "industry_40",
    ProjectSector.HEALTH.value: "industry_40",
    ProjectSector.EDUCATION.value: "industry_40",
    ProjectSector.RETAIL.value: "industry_40",
    ProjectSector.OTHER.value: "industry_40",
}

# Integrações cross-sector sugeridas por sector primário
_CROSS_LINKS: dict[str, tuple[str, ...]] = {
    "agri_tech": ("cross_sector", "infrastructure"),
    "industry_40": ("cross_sector", "esg"),
    "infrastructure": ("cross_sector", "agri_tech"),
    "mobility": ("cross_sector",),
    "tourism": ("esg", "cross_sector"),
}


class SectorModuleRegistry:
    """Resolve módulos setoriais para um projecto."""

    @staticmethod
    def get_module(code: str) -> SectorModule | None:
        return _ALL_MODULES.get(code)

    @staticmethod
    def primary_module_code(sector: str) -> str:
        key = (sector or ProjectSector.OTHER.value).lower()
        if not ProjectSector.is_valid(key):
            key = ProjectSector.OTHER.value
        return _PRIMARY_MODULE_BY_SECTOR.get(key, "industry_40")

    @staticmethod
    def resolve(sector: str) -> tuple[SectorModule, SectorModule, tuple[SectorModule, ...]]:
        """Retorna (primário, ESG, relacionados)."""
        primary_code = SectorModuleRegistry.primary_module_code(sector)
        primary = _ALL_MODULES[primary_code]
        esg = _ESG
        related_codes = _CROSS_LINKS.get(primary_code, ("esg",))
        related = tuple(_ALL_MODULES[c] for c in related_codes if c in _ALL_MODULES)
        return primary, esg, related

    @staticmethod
    def list_all() -> list[SectorModule]:
        return list(_ALL_MODULES.values())
