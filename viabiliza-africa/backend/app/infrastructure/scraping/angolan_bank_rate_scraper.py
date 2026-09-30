from __future__ import annotations



import logging

import re

from dataclasses import dataclass

from decimal import Decimal

from io import BytesIO



import requests



from app.domain.enums.financing_bank import FinancingBank

from app.infrastructure.scraping.agt_nif_lookup import parse_percent



logger = logging.getLogger(__name__)



HEADERS = {

    "User-Agent": (

        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "

        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

    ),

    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",

}





@dataclass(frozen=True)

class BankRateQuote:

    bank_code: str

    bank_name: str

    rate_percent: Decimal

    product_label: str

    source_url: str

    currency: str = "AOA"





# Fontes públicas oficiais / páginas de produto e preçários com taxa publicada

BANK_RATE_SOURCES: dict[str, list[dict]] = {

    FinancingBank.BFA.value: [

        {

            "url": "https://www.bfa.ao/pt/private-banking/financiamento/credito-colateral-bfa/",

            "label": "Crédito Colateral BFA",

            "prefer_sectors": (),

        },

        {

            "url": "https://www.bfa.ao/pt/empresas/credito/credito-de-campanha-agricola-bfa/",

            "label": "Crédito de Campanha Agrícola BFA (Aviso BNA 10/24)",

            "prefer_sectors": ("agriculture",),

        },

        {

            "url": "https://www.bfa.ao/pt/empresas/oferta-sectorial/credito-ao-investimento-ml-prazo/",

            "label": "Crédito ao Investimento M/L Prazo BFA",

            "prefer_sectors": ("industry", "agriculture"),

        },

    ],

    FinancingBank.BAI.value: [

        {

            "url": "https://www.bancobai.ao/pt/empresas",

            "label": "Soluções de crédito BAI Empresas",

            "prefer_sectors": (),

        },

        {

            "url": "https://www.bancobai.ao/",

            "label": "Taxas publicadas BAI",

            "prefer_sectors": (),

        },

    ],

    FinancingBank.BIC.value: [

        {

            "url": "https://www.bancobic.ao/inicio/empresas/index",

            "label": "Crédito empresas Banco BIC",

            "prefer_sectors": (),

        },

        {

            "url": "https://www.bancobic.ao/",

            "label": "Taxas publicadas Banco BIC",

            "prefer_sectors": (),

        },

    ],

    FinancingBank.ATL.value: [

        {

            "url": (

                "https://www.atlantico.ao/media/dbyd00r0/"

                "aviso-n%C2%BA-09-2024-cr%C3%A9dito-%C3%A0-habitac%C3%A3o-e-a-constru%C3%A7%C3%A3o.pdf"

            ),

            "label": "Crédito habitação/construção Atlântico (Aviso 09/2024)",

            "prefer_sectors": (),

            "kind": "pdf",

        },

        {

            "url": "https://www.atlantico.ao/pt/empresas/",

            "label": "Soluções empresas Millennium Atlântico",

            "prefer_sectors": (),

        },

    ],

    FinancingBank.SBA.value: [

        {

            "url": (

                "https://www.standardbank.co.ao/static_file/Angola/Home/Particulares/"

                "precarios/2025/Standard%20Bank%20Angola_Tabela%20de%20Pre%C3%A7%C3%A1rio_Particulares.pdf"

            ),

            "label": "Preçário Standard Bank Angola (Clientes Particulares)",

            "prefer_sectors": (),

            "kind": "pdf",

        },

        {

            "url": "https://www.standardbank.co.ao/angola/pt/Particulares",

            "label": "Portal Standard Bank Angola",

            "prefer_sectors": (),

        },

    ],

    FinancingBank.BPC.value: [

        {

            "url": "https://www.bpc.ao/",

            "label": "Taxas publicadas BPC",

            "prefer_sectors": (),

        },

    ],

    FinancingBank.BDA.value: [

        {

            "url": "https://www.bda.ao/",

            "label": "Taxas de juro publicadas BDA",

            "prefer_sectors": (),

        },

        {

            "url": "https://www.bda.ao/produtos-e-servicos/creditos/",

            "label": "Soluções de crédito BDA",

            "prefer_sectors": ("agriculture",),

        },

    ],

    FinancingBank.SOL.value: [

        {

            "url": (

                "https://www.bancosol.ao/hubfs/"

                "BSOL-%20Pre%C3%A7%C3%A1rio%20-%20Clientes%20Particulares%20e%20Outros%20Clientes.pdf"

                "?hsLang=pt"

            ),

            "label": "Preçário Banco Sol (Clientes Particulares)",

            "prefer_sectors": (),

            "kind": "pdf",

        },

        {

            "url": "https://www.bancosol.ao/pt/particulares/creditos/consumo",

            "label": "Crédito ao consumo Banco Sol",

            "prefer_sectors": (),

        },

    ],

    FinancingBank.BNI.value: [

        {

            "url": "https://www.bni.ao/pt/empresas",

            "label": "Crédito empresas BNI",

            "prefer_sectors": (),

        },

        {

            "url": "https://www.bni.ao/pt/particulares/creditos",

            "label": "Créditos particulares BNI",

            "prefer_sectors": (),

        },

    ],

    FinancingBank.KEVE.value: [

        {

            "url": "https://www.bancokeve.ao/",

            "label": "Taxas publicadas Banco Keve",

            "prefer_sectors": (),

            "verify_ssl": False,

        },

    ],

    FinancingBank.BCGA.value: [

        {

            "url": "https://www.caixaangola.ao/",

            "label": "Taxas publicadas Caixa Angola",

            "prefer_sectors": (),

        },

    ],

    FinancingBank.BCI.value: [

        {

            "url": "https://www.bci.ao/",

            "label": "Taxas publicadas BCI",

            "prefer_sectors": (),

        },

    ],

    FinancingBank.ECONOMICO.value: [

        {

            "url": "https://www.bancoeconomico.ao/pt/empresas/",

            "label": "Crédito empresas Banco Económico",

            "prefer_sectors": (),

        },

        {

            "url": "https://www.bancoeconomico.ao/",

            "label": "Taxas publicadas Banco Económico",

            "prefer_sectors": (),

        },

    ],

}



# Taxa de referência do sector produtivo (Aviso BNA 10/24) citada pelos bancos

BNA_PRODUCTIVE_CREDIT_RATE = Decimal("10")

BNA_HOUSING_MAX_RATE = Decimal("7")





class AngolanBankRateScraper:

    """Obtém taxas de juro/desconto a partir de páginas e preçários públicos dos bancos AO."""



    def list_banks(self) -> list[dict]:

        return [

            {

                "code": bank.value,

                "name": bank.label_pt,

                "website": bank.website,

                "logo": bank.logo_path,

            }

            for bank in FinancingBank

        ]



    def get_discount_rate(

        self, bank_code: str, *, sector: str | None = None

    ) -> BankRateQuote:

        if not FinancingBank.is_valid(bank_code):

            raise ValueError(

                f"Banco inválido. Valores: {', '.join(FinancingBank.values())}"

            )



        bank = FinancingBank(bank_code)

        sources = BANK_RATE_SOURCES.get(bank_code, [])

        if not sources:

            raise LookupError(f"Sem fontes de taxa configuradas para {bank.label_pt}")



        ordered = sorted(

            sources,

            key=lambda s: 0 if sector and sector in s.get("prefer_sectors", ()) else 1,

        )



        last_error: Exception | None = None

        for source in ordered:

            try:

                quote = self._scrape_source(bank, source, sector=sector)

                if quote:

                    return quote

            except Exception as exc:

                last_error = exc

                logger.warning(

                    "Falha a obter taxa %s em %s: %s", bank_code, source["url"], exc

                )



        raise LookupError(

            f"Não foi possível obter taxa real de {bank.label_pt} neste momento. "

            f"Consulte {bank.website}. "

            f"Detalhe: {last_error}"

        )



    def _scrape_source(

        self,

        bank: FinancingBank,

        source: dict,

        *,

        sector: str | None,

    ) -> BankRateQuote | None:

        verify = source.get("verify_ssl", True)

        response = requests.get(

            source["url"], headers=HEADERS, timeout=35, verify=verify

        )

        response.raise_for_status()



        kind = source.get("kind")

        content_type = (response.headers.get("content-type") or "").lower()

        if (

            kind == "pdf"

            or "pdf" in content_type

            or source["url"].lower().endswith(".pdf")

            or ".pdf?" in source["url"].lower()

        ):

            text = self._pdf_to_text(response.content)

        else:

            text = response.text



        rate = self._extract_best_rate(text, sector=sector)

        if rate is None:

            if re.search(r"(?is)aviso\s*(?:n[ºo.]?\s*)?10[\s/]*(?:24|2024)", text):

                rate = BNA_PRODUCTIVE_CREDIT_RATE

            elif re.search(r"(?is)aviso\s*(?:n[ºo.]?\s*)?09[\s/]*(?:24|2024)", text):

                rate = BNA_HOUSING_MAX_RATE

            else:

                return None



        return BankRateQuote(

            bank_code=bank.value,

            bank_name=bank.label_pt,

            rate_percent=rate,

            product_label=source["label"],

            source_url=source["url"],

        )



    def _pdf_to_text(self, content: bytes) -> str:

        try:

            from pypdf import PdfReader

        except ImportError as exc:

            raise RuntimeError(

                "Dependência pypdf necessária para ler preçários PDF dos bancos"

            ) from exc



        reader = PdfReader(BytesIO(content))

        pages = []

        for page in reader.pages[:20]:

            pages.append(page.extract_text() or "")

        return "\n".join(pages)



    def _extract_best_rate(self, text: str, *, sector: str | None) -> Decimal | None:

        candidates: list[tuple[int, Decimal]] = []



        patterns = [

            (14, r"(?is)taeg(?:\s|\n|<[^>]+>){0,40}?(\d{1,2}(?:[.,]\d{1,2})?)\s*%"),

            (

                12,

                r"(?is)taxa\s+de\s+juro(?:\s|<[^>]+>|\n){0,40}?"

                r"(\d{1,2}(?:[.,]\d{1,2})?)\s*%",

            ),

            (

                11,

                r"(?is)taxa\s+de\s+juro\s+nominal[^%]{0,80}?"

                r"(\d{1,2}(?:[.,]\d{1,2})?)\s*%",

            ),

            (10, r"(?is)taxa\s+bna[^%]{0,60}?(\d{1,2}(?:[.,]\d{1,2})?)\s*%"),

            (

                9,

                r"(?is)(?:sb\s*prime|indexante)[^%]{0,50}?"

                r"(\d{1,2}(?:[.,]\d{1,2})?)\s*%",

            ),

            (8, r"(?is)aviso[^%]{0,80}?(\d{1,2}(?:[.,]\d{1,2})?)\s*%"),

            (6, r"(?is)taxa[^%]{0,40}?(\d{1,2}(?:[.,]\d{1,2})?)\s*%"),

        ]



        for weight, pattern in patterns:

            for match in re.finditer(pattern, text):

                value = parse_percent(match.group(1))

                if value is not None:

                    candidates.append((weight, value))



        if not candidates:

            return None



        # Excluir comissões/impostos (<6,5%) e outliers (>40%)

        credit_like = [

            (w, v) for w, v in candidates if Decimal("6.5") <= v <= Decimal("40")

        ]

        if credit_like:

            candidates = credit_like



        target = Decimal("10") if sector == "agriculture" else Decimal("15")

        candidates.sort(

            key=lambda item: (item[0], -abs(item[1] - target)),

            reverse=True,

        )

        return candidates[0][1]


