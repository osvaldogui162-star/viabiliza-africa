"""Preços comerciais AOA — trimestral, semestral e anual (fonte única)."""

from __future__ import annotations

from decimal import Decimal
from typing import Literal

BillingPeriod = Literal["quarterly", "semiannual", "yearly"]

PROMOTION_DISCOUNT_PCT = 20

# Planos comercializados na página /planos (free mantém-se só para contas implícitas)
PUBLIC_PLAN_CODES = (
    "starter",
    "business",
    "enterprise",
    "academia_institutional",
    "government",
)

# Apenas planos self-service; Enterprise/Academia/Governo são contact_only.
ONLINE_CHECKOUT_PLAN_CODES = frozenset({"starter", "business"})

BILLING_PERIOD_DAYS: dict[BillingPeriod, int] = {
    "quarterly": 90,
    "semiannual": 180,
    "yearly": 365,
}

# fixed_aoa = preço actual; reference_aoa = preço anterior (base da campanha −20%)
PLAN_AOA_PRICING: dict[str, dict[str, dict[str, int]]] = {
    "starter": {
        "quarterly": {"fixed": 150_000, "reference": 187_500},
        "semiannual": {"fixed": 300_000, "reference": 375_000},
        "yearly": {"fixed": 550_000, "reference": 687_500},
    },
    "business": {
        "quarterly": {"fixed": 280_000, "reference": 350_000},
        "semiannual": {"fixed": 550_000, "reference": 600_000},
        "yearly": {"fixed": 950_000, "reference": 1_200_000},
    },
    "enterprise": {
        "quarterly": {"fixed": 350_000, "reference": 400_000},
        "semiannual": {"fixed": 650_000, "reference": 700_000},
        "yearly": {"fixed": 1_250_000, "reference": 1_400_000},
    },
    "academia_institutional": {
        "quarterly": {"fixed": 350_000, "reference": 437_500},
        "semiannual": {"fixed": 650_000, "reference": 812_500},
        "yearly": {"fixed": 1_250_000, "reference": 1_562_500},
    },
    "government": {
        "quarterly": {"fixed": 1_000_000, "reference": 1_250_000},
        "semiannual": {"fixed": 2_000_000, "reference": 2_500_000},
        "yearly": {"fixed": 3_000_000, "reference": 3_750_000},
    },
}

PLAN_RECOMMENDATION: dict[str, dict[str, str]] = {
    "starter": {
        "headline_pt": "Ideal para começar com rigor bancário",
        "headline_en": "Ideal to start with bank-grade rigour",
        "reason_pt": (
            "Se gere até 20 estudos e precisa de scraping moderado, o Starter "
            "equilibra custo e credibilidade perante investidores."
        ),
        "reason_en": (
            "If you run up to 20 studies and need moderate scraping, Starter "
            "balances cost and credibility with investors."
        ),
        "upgrade_pt": "Precisa de equipa ou API bancária? Considere o Business.",
        "upgrade_en": "Need a team or bank API? Consider Business.",
    },
    "business": {
        "headline_pt": "O sweet spot para consultoras em crescimento",
        "headline_en": "The sweet spot for growing consultancies",
        "reason_pt": (
            "Projetos ilimitados, 500 itens de scraping/mês e integrações ERP "
            "reduzem o tempo até ao relatório aprovado pelo banco."
        ),
        "reason_en": (
            "Unlimited projects, 500 scraping items/month and ERP integrations "
            "shorten time to bank-ready reports."
        ),
        "upgrade_pt": "Operação multi-sede ou banca? O Enterprise desbloqueia onboarding dedicado.",
        "upgrade_en": "Multi-site or banking ops? Enterprise unlocks dedicated onboarding.",
    },
    "enterprise": {
        "headline_pt": "Escala institucional com suporte dedicado",
        "headline_en": "Institutional scale with dedicated support",
        "reason_pt": (
            "Para bancos, holdings e grandes consultoras que exigem utilizadores "
            "ilimitados, consultoria incluída e SLA de 4 horas."
        ),
        "reason_en": (
            "For banks, holdings and large firms needing unlimited users, "
            "included consulting and a 4-hour SLA."
        ),
        "upgrade_pt": "Campanha activa: aproveite 20% sobre o preço de referência.",
        "upgrade_en": "Active campaign: enjoy 20% off the reference price.",
    },
    "academia_institutional": {
        "headline_pt": "Formação e investigação com licença institucional",
        "headline_en": "Teaching and research with an institutional licence",
        "reason_pt": (
            "Licenciamento para docentes e alunos, manual académico e certificação "
            "de competências em viabilidade."
        ),
        "reason_en": (
            "Licence for faculty and students, academic manual and "
            "feasibility skills certification."
        ),
        "upgrade_pt": "Combine com parceria MOU para condições de volume.",
        "upgrade_en": "Combine with an MOU partnership for volume terms.",
    },
    "government": {
        "headline_pt": "Conformidade e integração para o sector público",
        "headline_en": "Compliance and integration for the public sector",
        "reason_pt": (
            "Relatórios personalizados, integração com sistemas governamentais "
            "e suporte 24/7 para programas de investimento público."
        ),
        "reason_en": (
            "Custom reports, government system integration and 24/7 support "
            "for public investment programmes."
        ),
        "upgrade_pt": "Contacte comercial para proposta formal e SLA contratual.",
        "upgrade_en": "Contact sales for a formal proposal and contractual SLA.",
    },
}


def aoa_to_usd_display(aoa: int) -> Decimal:
    """Taxa de referência UI (1 USD = 1 000 AOA)."""
    return (Decimal(aoa) / Decimal("1000")).quantize(Decimal("0.01"))


def fixed_aoa(plan_code: str, period: BillingPeriod) -> int:
    return PLAN_AOA_PRICING[plan_code][period]["fixed"]


def reference_aoa(plan_code: str, period: BillingPeriod) -> int:
    return PLAN_AOA_PRICING[plan_code][period]["reference"]


def promotional_aoa(plan_code: str, period: BillingPeriod) -> int:
    ref = reference_aoa(plan_code, period)
    return int((Decimal(ref) * (Decimal("100") - Decimal(PROMOTION_DISCOUNT_PCT)) / Decimal("100")).quantize(Decimal("1")))
