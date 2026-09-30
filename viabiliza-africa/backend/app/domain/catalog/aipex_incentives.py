"""Incentivos fiscais AIPEX por sector (referência simplificada para viabilidade)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AipexIncentive:
    code: str
    title: str
    description: str
    benefit_type: str
    sectors: tuple[str, ...]


AIPEX_INCENTIVES: tuple[AipexIncentive, ...] = (
    AipexIncentive(
        "beneficio_reinvestimento",
        "Benefício de Reinvestimento",
        "Redução de imposto sobre lucro reinvestido em activos fixos tangíveis.",
        "fiscal",
        ("manufacturing", "agriculture", "technology", "energy", "construction"),
    ),
    AipexIncentive(
        "deducao_investimento",
        "Dedução de Investimento",
        "Dedução acelerada de investimentos elegíveis em zonas prioritárias.",
        "fiscal",
        ("manufacturing", "agriculture", "tourism", "health", "education"),
    ),
    AipexIncentive(
        "isencao_importacao",
        "Isenção de direitos aduaneiros",
        "Isenção ou redução de direitos aduaneiros para equipamentos CAPEX.",
        "aduaneiro",
        ("manufacturing", "technology", "energy", "mining", "health"),
    ),
    AipexIncentive(
        "iva_capex",
        "IVA — equipamentos de investimento",
        "Tratamento preferencial de IVA em bens de capital importados ou adquiridos localmente.",
        "fiscal",
        ("manufacturing", "retail", "transport", "construction", "real_estate"),
    ),
    AipexIncentive(
        "zona_desenvolvimento",
        "Zona de Desenvolvimento Económico",
        "Benefícios adicionais para projectos fora de Luanda/Benguela metropolitano.",
        "regional",
        ("agriculture", "tourism", "manufacturing", "mining", "energy"),
    ),
    AipexIncentive(
        "formacao_local",
        "Formação e emprego local",
        "Incentivos ligados à criação de postos de trabalho e formação técnica.",
        "social",
        ("services", "technology", "education", "health", "other"),
    ),
)


def list_aipex_incentives_for_sector(sector: str) -> list[dict]:
    code = sector.lower().strip()
    return [
        {
            "code": item.code,
            "title": item.title,
            "description": item.description,
            "benefit_type": item.benefit_type,
            "applicable": code in item.sectors or "other" in item.sectors,
        }
        for item in AIPEX_INCENTIVES
        if code in item.sectors or "other" in item.sectors
    ]
