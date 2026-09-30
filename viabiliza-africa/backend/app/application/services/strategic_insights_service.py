"""Geração automática de Missão, Visão, Valores, SWOT e riscos."""

from __future__ import annotations

from decimal import Decimal

from app.domain.catalog.aipex_incentives import list_aipex_incentives_for_sector
from app.domain.entities.project import Project


class StrategicInsightsService:
    def generate(self, project: Project) -> dict:
        sector_label = project.sector.label_pt
        company = project.company_name.strip()
        location = project.company_municipality or project.company_province or "Angola"
        investment = project.investment_amount

        mission = (
            f"Desenvolver e operar {project.name} em {location}, "
            f"entregando valor sustentável no sector {sector_label} "
            f"com impacto económico e social positivo em Angola."
        )
        vision = (
            f"Tornar-se referência em {sector_label} em Angola, "
            f"reconhecida pela qualidade, eficiência operacional e contribuição "
            f"para o desenvolvimento económico nacional."
        )
        core_values = [
            "Integridade e transparência",
            "Excelência operacional",
            "Inovação orientada ao mercado angolano",
            "Responsabilidade social e ambiental",
            "Foco no cliente e nos stakeholders",
        ]

        swot = self._build_swot(project, sector_label, investment)
        risks = self._build_risks(project, sector_label)
        aipex = list_aipex_incentives_for_sector(project.sector.value)

        return {
            "mission": mission,
            "vision": vision,
            "core_values": core_values,
            "swot_analysis": swot,
            "risk_register": risks,
            "aipex_incentives": aipex,
        }

    def _build_swot(self, project: Project, sector_label: str, investment: Decimal) -> dict:
        return {
            "strengths": [
                f"Projecto estruturado com investimento de {investment:,.0f} {project.currency.value}",
                f"Localização em {project.company_municipality or project.company_province or 'Angola'}",
                f"Actividade alinhada ao sector {sector_label}",
                "Processo de viabilidade rastreável com dados de mercado",
            ],
            "weaknesses": [
                "Dependência de condições macroeconómicas angolanas",
                "Necessidade de capital de giro inicial",
                "Curva de aprendizagem operacional no arranque",
            ],
            "opportunities": [
                "Crescimento da procura no sector em Angola",
                "Incentivos fiscais AIPEX aplicáveis",
                "Digitalização e modernização de processos",
                "Parcerias com fornecedores locais credíveis",
            ],
            "threats": [
                "Volatilidade cambial (Kwanza)",
                "Concorrência de operadores estabelecidos",
                "Pressão inflacionária nos custos OPEX",
                "Alterações regulatórias ou aduaneiras",
            ],
        }

    def _build_risks(self, project: Project, sector_label: str) -> list[dict]:
        return [
            {
                "code": "macro_fx",
                "title": "Risco cambial",
                "severity": "alta",
                "mitigation": "Contratos indexados e cobertura parcial de importações CAPEX.",
            },
            {
                "code": "market_demand",
                "title": "Risco de procura",
                "severity": "média",
                "mitigation": "Validação comercial prévia e cenários pessimista/base/optimista.",
            },
            {
                "code": "opex_inflation",
                "title": "Inflação operacional",
                "severity": "média",
                "mitigation": "Cláusulas de revisão de preços e contratos plurianuais com fornecedores.",
            },
            {
                "code": "regulatory",
                "title": "Risco regulatório / AIPEX",
                "severity": "média",
                "mitigation": "Acompanhamento de elegibilidade fiscal e documentação de compliance.",
            },
            {
                "code": "execution",
                "title": "Risco de execução",
                "severity": "média",
                "mitigation": f"Cronograma faseado e equipa técnica especializada em {sector_label}.",
            },
        ]
