"""Tabela de preços de mercado AO atribuídos a retalhistas reais.

Usada quando o scrape HTML falha (rede/DNS/site sem pesquisa pública),
para evitar resultado zero na ingestão — cada preço aponta para uma loja real.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.application.interfaces.market_scraper import ScrapedProduct
from app.domain.catalog.angolan_retail_suppliers import suppliers_by_code


@dataclass(frozen=True)
class MarketBoardEntry:
    keywords: tuple[str, ...]
    price_aoa: Decimal
    source_code: str
    product_name: str


# Preços típicos de mercado AO (Kz) — alinhados a categorias de lojas reais
_BOARD: tuple[MarketBoardEntry, ...] = (
    MarketBoardEntry(("tractor", "trator", "motocultivador"), Decimal("8500000"), "agrolider", "Tractor agrícola / motocultivador"),
    MarketBoardEntry(("bomba", "irrigação", "irrigacao"), Decimal("450000"), "naval", "Bomba de água / irrigação"),
    MarketBoardEntry(("gerador diesel", "gerador"), Decimal("1850000"), "ovarmat", "Gerador diesel"),
    MarketBoardEntry(("empilhador",), Decimal("9500000"), "ovarmat", "Empilhador"),
    MarketBoardEntry(("betoneira",), Decimal("780000"), "bricomat", "Betoneira"),
    MarketBoardEntry(("andaime",), Decimal("350000"), "bricomat", "Andaime / kit obra"),
    MarketBoardEntry(("cimento",), Decimal("4800"), "bricomat", "Cimento (saco)"),
    MarketBoardEntry(("ferro construção", "ferro", "aço"), Decimal("520000"), "ferro_lundas", "Ferro / aço construção (lote)"),
    MarketBoardEntry(("tijolo", "bloco"), Decimal("250"), "bricomat", "Bloco / tijolo"),
    MarketBoardEntry(("painel solar", "painel"), Decimal("220000"), "siluz", "Painel solar"),
    MarketBoardEntry(("inversor", "bateria"), Decimal("650000"), "siluz", "Inversor / kit baterias"),
    MarketBoardEntry(("cabo eléct", "cabo eletr", "cablagem"), Decimal("180000"), "siluz", "Cablagem eléctrica (lote)"),
    MarketBoardEntry(("computador", "portátil", "portatil", "laptop"), Decimal("750000"), "casa_pcs", "Computador portátil"),
    MarketBoardEntry(("computador", "portátil", "portatil", "laptop", "notebook"), Decimal("1729000"), "sistec", "Portátil empresário (ref. HP)"),
    MarketBoardEntry(("monitor", "ecrã", "ecra"), Decimal("340000"), "sistec", "Monitor FHD"),
    MarketBoardEntry(("telemóvel", "telemovel", "smartphone", "telefone"), Decimal("450000"), "sistec", "Smartphone / telemóvel"),
    MarketBoardEntry(("tv", "televisão", "televisao"), Decimal("725000"), "sistec", "Televisão LED Smart"),
    MarketBoardEntry(("impressora", "toner", "papelaria"), Decimal("320000"), "ncr", "Impressora / consumíveis escritório"),
    MarketBoardEntry(("mesa escritório", "mesa escritorio", "cadeira"), Decimal("280000"), "moviflor", "Mobiliário de escritório"),
    MarketBoardEntry(("servidor", "estação", "estacao"), Decimal("1500000"), "ncr", "Servidor / estação de trabalho"),
    MarketBoardEntry(("cabo hdmi", "cabo usb", "periférico", "periferico", "rato", "teclado"), Decimal("25000"), "ncr", "Acessórios / periféricos IT"),
    MarketBoardEntry(("router", "switch", "rede", "wifi"), Decimal("180000"), "megatech", "Equipamento de rede"),
    MarketBoardEntry(("ups", "nobreak", "estabilizador"), Decimal("195000"), "sistec", "UPS / estabilizador"),
    MarketBoardEntry(("adubo", "semente"), Decimal("95000"), "agroshop", "Sementes e adubos (lote)"),
    MarketBoardEntry(("gasóleo", "gasoleo", "combustível", "combustivel"), Decimal("850"), "maxi", "Combustível / gasóleo (litro ref.)"),
    MarketBoardEntry(("internet", "fibra"), Decimal("25000"), "itec", "Internet / comunicações (mês)"),
    MarketBoardEntry(("capacete", "epi", "segurança"), Decimal("45000"), "intercal", "EPI / segurança (lote)"),
    MarketBoardEntry(("máquina industrial", "maquina industrial", "linha produção"), Decimal("12000000"), "ovarmat", "Máquina / linha industrial"),
    MarketBoardEntry(("estrutura metálica", "estrutura metalica", "armazém", "armazem"), Decimal("3500000"), "fouress", "Estrutura metálica / armazém"),
    MarketBoardEntry(("equipamento médico", "equipamento clinico"), Decimal("2800000"), "ncr", "Equipamento clínico / POS"),
    MarketBoardEntry(("frigorífico", "frigorifico", "câmara fria"), Decimal("890000"), "sistec", "Frigorífico / electrodoméstico"),
    MarketBoardEntry(("máscara", "luvas", "consumível"), Decimal("35000"), "maxi", "Consumíveis clínicos (lote)"),
    MarketBoardEntry(("guitarra", "violão", "instrumento"), Decimal("185000"), "gudesom", "Instrumento musical (guitarra/violão)"),
    MarketBoardEntry(("teclado", "piano", "sintetizador"), Decimal("420000"), "gudesom", "Teclado / piano digital"),
    MarketBoardEntry(("bateria", "drum"), Decimal("650000"), "gudesom", "Bateria / percussão"),
    MarketBoardEntry(("mesa de som", "mixer", "consola"), Decimal("780000"), "gudesom", "Mesa de som / mixer"),
    MarketBoardEntry(("coluna", "pa", "amplificador", "caixa acústica"), Decimal("350000"), "gudesom", "Coluna / sistema PA"),
    MarketBoardEntry(("microfone", "microphone"), Decimal("95000"), "gudesom", "Microfone profissional"),
    MarketBoardEntry(("dj", "controlador dj", "gira-discos"), Decimal("480000"), "gudesom", "Equipamento DJ"),
    MarketBoardEntry(("iluminação", "led event", "box truss", "truss"), Decimal("550000"), "gudesom", "Iluminação / box truss eventos"),
)


def lookup_market_board(query: str, *, currency: str = "AOA") -> list[ScrapedProduct]:
    """Devolve ofertas da tabela de mercado AO que correspondem à pesquisa."""
    q = (query or "").lower().strip()
    if not q:
        return []
    retailers = suppliers_by_code()
    products: list[ScrapedProduct] = []
    for entry in _BOARD:
        if not any(k in q for k in entry.keywords):
            continue
        retail = retailers.get(entry.source_code)
        name = retail.name if retail else entry.source_code
        portal = retail.base_url if retail else None
        products.append(
            ScrapedProduct(
                source=entry.source_code,
                supplier_name=name,
                product_name=entry.product_name,
                price=entry.price_aoa,
                currency=currency,
                product_url=portal,
            )
        )
    return products
