"""Catálogo de retalhistas e fornecedores angolanos para ingestão de preços."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetailSupplier:
    """Fornecedor/retalhista local usado como fonte de preços."""

    code: str
    name: str
    base_url: str
    groups: tuple[str, ...]
    """Grupos: supermarket, construction, electrical, it, furniture,
    auto, auto_parts, pharmacy, appliances, stationery, agriculture, epi,
    plumbing, music."""
    search_urls: tuple[str, ...] = ()
    """Templates com {q}; vazio = ainda sem loja online scrapável."""
    scrape_enabled: bool = False
    city_note: str | None = None


# Mapa: categoria do catálogo setorial → grupos de retalhistas preferidos
CATALOG_CATEGORY_TO_GROUPS: dict[str, tuple[str, ...]] = {
    "Documentação": (),
    "IT": ("it", "appliances"),
    "Mobiliário": ("furniture", "appliances"),
    "Telecom": ("it", "appliances"),
    "Serviços": (),
    "Equipamento": ("construction", "agriculture", "electrical", "appliances", "auto", "music"),
    "Infraestrutura": ("construction", "plumbing", "electrical"),
    "Insumos": ("supermarket", "agriculture"),
    "Energia": ("electrical", "construction", "appliances"),
    "Pessoal": (),
    "Logística": ("auto", "auto_parts"),
    "Segurança": ("epi", "construction", "electrical"),
    "Matérias-primas": ("supermarket", "construction", "agriculture"),
    "Produção": ("construction", "electrical", "agriculture"),
    "Operação": ("supermarket", "appliances", "pharmacy"),
    "Áudio": ("music", "electrical", "appliances"),
    "Ambientação": ("music", "furniture", "appliances"),
    "Eventos": ("music", "electrical", "appliances"),
}

# Marketplaces gerais — sempre consultados em paralelo
GENERAL_MARKETPLACE_CODES: tuple[str, ...] = (
    "kikolo",
    "socia",
    "praca_digital",
    "jumia",
    "jiji",
)


# ---------------------------------------------------------------------------
# 1. Supermercados / retalho alimentar
# ---------------------------------------------------------------------------
_SUPERMARKETS: tuple[RetailSupplier, ...] = (
    RetailSupplier("candando", "Candando Viana", "https://www.candando.co.ao", ("supermarket",), city_note="Viana"),
    RetailSupplier("angomart", "AngoMart", "https://www.angomart.co.ao", ("supermarket", "appliances")),
    RetailSupplier(
        "maxi",
        "Maxi Supermarket",
        "https://www.maxi.co.ao",
        ("supermarket",),
        search_urls=("https://www.maxi.co.ao/?s={q}",),
        scrape_enabled=True,
    ),
    RetailSupplier(
        "shoprite",
        "Shoprite Angola",
        "https://shoprite.co.ao",
        ("supermarket",),
        search_urls=("https://shoprite.co.ao/?s={q}", "https://www.shoprite.co.ao/search?q={q}"),
        scrape_enabled=True,
    ),
    RetailSupplier("nosso_super", "Nosso Super", "https://www.nossosuper.co.ao", ("supermarket",)),
    RetailSupplier("fresmart", "Fresmart", "https://www.fresmart.co.ao", ("supermarket",)),
    RetailSupplier("martal", "Martal", "https://www.martal.co.ao", ("supermarket",)),
    RetailSupplier("alimenta_ao", "Alimenta Angola", "https://www.alimentaangola.co.ao", ("supermarket",)),
    RetailSupplier("intermarket", "Intermarket", "https://www.intermarket.co.ao", ("supermarket",)),
    RetailSupplier("megamart", "Megamart", "https://www.megamart.co.ao", ("supermarket",)),
    RetailSupplier("nossa_casa", "Nossa Casa", "https://www.nossacasa.co.ao", ("supermarket", "furniture")),
    RetailSupplier("bompreco", "Bompreço", "https://www.bompreco.co.ao", ("supermarket",)),
    RetailSupplier("continente_ao", "Continente Angola", "https://www.continente.co.ao", ("supermarket",)),
    RetailSupplier("ok_super", "OK Supermercados", "https://www.ok.co.ao", ("supermarket",)),
    RetailSupplier("usave", "Usave", "https://www.usave.co.ao", ("supermarket",)),
    RetailSupplier("casa_frescos", "Casa dos Frescos", "https://www.casadosfrescos.co.ao", ("supermarket",)),
)

# ---------------------------------------------------------------------------
# 2. Materiais de construção
# ---------------------------------------------------------------------------
_CONSTRUCTION: tuple[RetailSupplier, ...] = (
    RetailSupplier(
        "bricomat",
        "Bricomat Mutamba",
        "https://www.bricomat.co.ao",
        ("construction", "plumbing", "electrical", "epi"),
        search_urls=("https://www.bricomat.co.ao/?s={q}", "https://bricomat.co.ao/search?q={q}"),
        scrape_enabled=True,
        city_note="Mutamba",
    ),
    RetailSupplier(
        "ovarmat",
        "Ovarmat Angola",
        "https://www.ovarmatangola.com",
        ("construction", "plumbing", "epi"),
        search_urls=(
            "https://www.ovarmatangola.com/?s={q}",
            "https://www.ovarmatangola.com/search?q={q}",
            "https://www.ovarmatangola.com/pesquisar?q={q}",
        ),
        scrape_enabled=True,
        city_note="Viana / Benfica",
    ),
    RetailSupplier("dama", "Dama", "https://www.dama.co.ao", ("construction", "plumbing", "furniture")),
    RetailSupplier(
        "intercal",
        "Intercal",
        "https://www.intercal.co.ao",
        ("construction", "electrical", "epi", "plumbing"),
        search_urls=("https://www.intercal.co.ao/?s={q}",),
        scrape_enabled=True,
    ),
    RetailSupplier(
        "o_index",
        "O-Index",
        "https://www.o-index.co.ao",
        ("construction", "electrical", "epi", "plumbing"),
        search_urls=("https://www.o-index.co.ao/?s={q}", "https://oindex.co.ao/?s={q}"),
        scrape_enabled=True,
    ),
    RetailSupplier(
        "ferro_lundas",
        "Ferro-Lundas",
        "https://www.ferrolundas.co.ao",
        ("construction", "epi"),
        search_urls=("https://www.ferrolundas.co.ao/?s={q}",),
        scrape_enabled=True,
    ),
    RetailSupplier("nour", "Nour Company", "https://www.nourcompany.co.ao", ("construction",)),
    RetailSupplier("fouress", "Fouress Group", "https://www.fouress.co.ao", ("construction",)),
)

# ---------------------------------------------------------------------------
# 3. Material elétrico
# ---------------------------------------------------------------------------
_ELECTRICAL: tuple[RetailSupplier, ...] = (
    RetailSupplier(
        "siluz",
        "SILUZ Angola",
        "https://siluzangola.com",
        ("electrical",),
        search_urls=(
            "https://siluzangola.com/?s={q}",
            "https://www.siluzangola.com/search?q={q}",
            "https://siluzangola.com/loja/?s={q}",
        ),
        scrape_enabled=True,
        city_note="São Paulo / Viana",
    ),
    RetailSupplier(
        "soletric",
        "Soletric",
        "https://www.soletric.co.ao",
        ("electrical", "epi"),
        search_urls=("https://www.soletric.co.ao/?s={q}",),
        scrape_enabled=True,
    ),
)

# ---------------------------------------------------------------------------
# 4. Informática e tecnologia
# ---------------------------------------------------------------------------
_IT: tuple[RetailSupplier, ...] = (
    RetailSupplier(
        "ncr",
        "NCR Angola",
        "https://www.ncrangola.com",
        ("it", "appliances", "stationery"),
        search_urls=(
            "https://www.ncrangola.com/search?q={q}",
            "https://www.ncrangola.com/informatica?q={q}",
        ),
        scrape_enabled=True,
        city_note="Talatona / Luanda",
    ),
    RetailSupplier(
        "sistec",
        "SISTEC Lojas",
        "https://loja.sistec.co.ao",
        ("it", "appliances"),
        search_urls=(
            "https://loja.sistec.co.ao/?s={q}",
            "https://loja.sistec.co.ao/?post_type=product&s={q}",
            "https://loja.sistec.co.ao/search?q={q}",
        ),
        scrape_enabled=True,
        city_note="Maculusso / rede nacional",
    ),
    RetailSupplier(
        "itec",
        "ITEC LDA Alvalade",
        "https://www.itec.co.ao",
        ("it",),
        search_urls=("https://www.itec.co.ao/?s={q}",),
        scrape_enabled=True,
        city_note="Alvalade",
    ),
    RetailSupplier(
        "zicai",
        "Zicai Grupo Infornet Viana",
        "https://www.zicai.co.ao",
        ("it",),
        city_note="Viana",
    ),
    RetailSupplier(
        "megatech",
        "Megatech",
        "https://www.megatech.co.ao",
        ("it", "appliances"),
        search_urls=("https://www.megatech.co.ao/?s={q}",),
        scrape_enabled=True,
    ),
    RetailSupplier(
        "casa_pcs",
        "Casa dos Computadores",
        "https://www.casadoscomputadores.co.ao",
        ("it",),
        search_urls=("https://www.casadoscomputadores.co.ao/?s={q}",),
        scrape_enabled=True,
    ),
)

# ---------------------------------------------------------------------------
# 5. Móveis e decoração
# ---------------------------------------------------------------------------
_FURNITURE: tuple[RetailSupplier, ...] = (
    RetailSupplier(
        "moviflor",
        "Moviflor Angola",
        "https://moviflor.ao",
        ("furniture",),
        search_urls=(
            "https://moviflor.ao/?s={q}",
            "https://www.moviflor.ao/search?q={q}",
            "https://moviflor.ao/loja/?s={q}",
        ),
        scrape_enabled=True,
    ),
    RetailSupplier("dama_home", "Dama Home", "https://www.damahome.co.ao", ("furniture",)),
    RetailSupplier("casa_moveis", "Casa dos Móveis", "https://www.casadosmoveis.co.ao", ("furniture",)),
    RetailSupplier("decor_ao", "Decor Angola", "https://www.decorangola.co.ao", ("furniture",)),
    RetailSupplier("casa_design", "Casa Design", "https://www.casadesign.co.ao", ("furniture",)),
)

# ---------------------------------------------------------------------------
# 6. Automóveis
# ---------------------------------------------------------------------------
_AUTO: tuple[RetailSupplier, ...] = (
    RetailSupplier(
        "toyota_ao",
        "Toyota Angola / CFAO",
        "https://www.cfaomotorsangola.com",
        ("auto", "auto_parts"),
        search_urls=("https://www.cfaomotorsangola.com/?s={q}",),
        scrape_enabled=True,
    ),
    RetailSupplier("cfao", "CFAO Mobility Angola", "https://www.cfaomotorsangola.com", ("auto", "auto_parts")),
    RetailSupplier("hyundai_ao", "Hyundai Angola", "https://www.hyundai.co.ao", ("auto",)),
    RetailSupplier("nissan_ao", "Nissan Angola", "https://www.nissan.co.ao", ("auto",)),
    RetailSupplier("kia_ao", "Kia Angola", "https://www.kia.co.ao", ("auto",)),
    RetailSupplier("mercedes_ao", "Mercedes-Benz Angola", "https://www.mercedes-benz.co.ao", ("auto",)),
    RetailSupplier("auto_sueco", "Auto Sueco", "https://www.autosueco.co.ao", ("auto",)),
    RetailSupplier("renault_ao", "Renault Angola", "https://www.renault.co.ao", ("auto",)),
    RetailSupplier("ford_ao", "Ford Angola", "https://www.ford.co.ao", ("auto",)),
)

# ---------------------------------------------------------------------------
# 7. Peças automóveis
# ---------------------------------------------------------------------------
_AUTO_PARTS: tuple[RetailSupplier, ...] = (
    RetailSupplier("auto_koka", "Auto Koka", "https://www.autokoka.co.ao", ("auto_parts",)),
    RetailSupplier(
        "auto_pecas_vn",
        "Auto Peças Viana",
        "https://www.autopecasviana.co.ao",
        ("auto_parts",),
        city_note="Viana",
    ),
    RetailSupplier("casa_pecas", "Casa das Peças", "https://www.casadaspecas.co.ao", ("auto_parts",)),
    RetailSupplier("lubriang", "Lubriang", "https://www.lubriang.co.ao", ("auto_parts",)),
    RetailSupplier("auto_stop", "Auto Stop", "https://www.autostop.co.ao", ("auto_parts",)),
)

# ---------------------------------------------------------------------------
# 8. Farmácias
# ---------------------------------------------------------------------------
_PHARMACY: tuple[RetailSupplier, ...] = (
    RetailSupplier("farm_central", "Farmácia Central", "https://www.farmaciacentral.co.ao", ("pharmacy",)),
    RetailSupplier("farm_popular", "Farmácia Popular", "https://www.farmaciapopular.co.ao", ("pharmacy",)),
    RetailSupplier("farm_cristal", "Farmácia Cristal", "https://www.farmaciacristal.co.ao", ("pharmacy",)),
    RetailSupplier("farm_universal", "Farmácia Universal", "https://www.farmaciauniversal.co.ao", ("pharmacy",)),
    RetailSupplier("farm_kianda", "Farmácia Kianda", "https://www.farmaciakianda.co.ao", ("pharmacy",)),
    RetailSupplier("farm_nacional", "Farmácia Nacional", "https://www.farmacianacional.co.ao", ("pharmacy",)),
)

# ---------------------------------------------------------------------------
# 9. Eletrodomésticos
# ---------------------------------------------------------------------------
_APPLIANCES: tuple[RetailSupplier, ...] = (
    RetailSupplier(
        "arreiou",
        "Arreiou",
        "https://arreiou.com",
        ("appliances", "supermarket"),
        search_urls=("https://arreiou.com/?s={q}", "https://www.arreiou.com/search?q={q}"),
        scrape_enabled=True,
    ),
    RetailSupplier("bestmarket", "Bestmarket", "https://www.bestmarket.co.ao", ("appliances",)),
    RetailSupplier("casa_eletros", "Casa dos Eletrodomésticos", "https://www.casadoseletrodomesticos.co.ao", ("appliances",)),
    RetailSupplier("megastore", "Megastore", "https://www.megastore.co.ao", ("appliances",)),
)

# ---------------------------------------------------------------------------
# 10. Papelarias
# ---------------------------------------------------------------------------
_STATIONERY: tuple[RetailSupplier, ...] = (
    RetailSupplier(
        "escolar_ed",
        "Livraria Escolar Editora",
        "https://www.escolareditora.co.ao",
        ("stationery",),
        search_urls=("https://www.escolareditora.co.ao/?s={q}",),
        scrape_enabled=True,
    ),
    RetailSupplier("papel_univ", "Papelaria Universal", "https://www.papelariauniversal.co.ao", ("stationery",)),
    RetailSupplier("papel_nova", "Papelaria Nova", "https://www.papelarianova.co.ao", ("stationery",)),
)

# ---------------------------------------------------------------------------
# 11. Agricultura
# ---------------------------------------------------------------------------
_AGRICULTURE: tuple[RetailSupplier, ...] = (
    RetailSupplier(
        "naval",
        "Naval",
        "https://www.naval.co.ao",
        ("agriculture",),
        search_urls=("https://www.naval.co.ao/?s={q}",),
        scrape_enabled=True,
    ),
    RetailSupplier(
        "agrolider",
        "Agrolíder",
        "https://www.agrolider.co.ao",
        ("agriculture",),
        search_urls=("https://www.agrolider.co.ao/?s={q}",),
        scrape_enabled=True,
    ),
    RetailSupplier("agrocampo", "AgroCampo", "https://www.agrocampo.co.ao", ("agriculture",)),
    RetailSupplier(
        "agroshop",
        "Agroshop Angola",
        "https://www.agroshop.co.ao",
        ("agriculture",),
        search_urls=("https://www.agroshop.co.ao/?s={q}",),
        scrape_enabled=True,
    ),
)


# ---------------------------------------------------------------------------
# 12. Música, áudio profissional e eventos
# ---------------------------------------------------------------------------
_MUSIC: tuple[RetailSupplier, ...] = (
    RetailSupplier(
        "gudesom",
        "GudeSom Angola",
        "https://gudesom.com",
        ("music", "electrical"),
        search_urls=(
            "https://gudesom.com/?s={q}",
            "https://gudesom.com/search?q={q}",
        ),
        scrape_enabled=True,
        city_note="Viana / Av. Comandante Valódia",
    ),
    RetailSupplier(
        "iscotec_music",
        "Iscotec Music",
        "https://www.iscotec.co.ao",
        ("music",),
        city_note="Luanda",
    ),
    RetailSupplier(
        "vens_music",
        "VENS Music",
        "https://www.vensmusic.co.ao",
        ("music",),
        city_note="Luanda",
    ),
    RetailSupplier(
        "musicomania",
        "Musicomania",
        "https://www.musicomania.co.ao",
        ("music",),
        city_note="Bungo / Luanda",
    ),
    RetailSupplier(
        "king_kong_music",
        "King Kong Music",
        "https://www.kingkongmusic.co.ao",
        ("music", "appliances"),
        city_note="Luanda",
    ),
    RetailSupplier(
        "casa_musica_ao",
        "Casa da Música Angola",
        "https://www.casadamusica.co.ao",
        ("music",),
        city_note="Luanda",
    ),
)


ALL_RETAIL_SUPPLIERS: tuple[RetailSupplier, ...] = (
    *_SUPERMARKETS,
    *_CONSTRUCTION,
    *_ELECTRICAL,
    *_IT,
    *_FURNITURE,
    *_AUTO,
    *_AUTO_PARTS,
    *_PHARMACY,
    *_APPLIANCES,
    *_STATIONERY,
    *_AGRICULTURE,
    *_MUSIC,
)


def suppliers_by_code() -> dict[str, RetailSupplier]:
    return {s.code: s for s in ALL_RETAIL_SUPPLIERS}


def scrapable_suppliers() -> list[RetailSupplier]:
    return [s for s in ALL_RETAIL_SUPPLIERS if s.scrape_enabled and s.search_urls]


def codes_for_catalog_category(category: str, *, limit: int = 8) -> list[str]:
    """Códigos de retalhistas preferidos para uma categoria de catálogo."""
    groups = CATALOG_CATEGORY_TO_GROUPS.get(category, ())
    if not groups:
        return []
    group_set = set(groups)
    scrapable = {s.code for s in scrapable_suppliers()}
    result: list[str] = []

    # 1) Um retalhista (preferir scrapável) por cada grupo relevante
    for group in groups:
        candidates = [s for s in ALL_RETAIL_SUPPLIERS if group in s.groups]
        candidates.sort(key=lambda s: (0 if s.code in scrapable else 1, s.name))
        for supplier in candidates:
            if supplier.code not in result:
                result.append(supplier.code)
                break

    # 2) Completar com outros scrapáveis do conjunto de grupos
    extras = [
        s
        for s in ALL_RETAIL_SUPPLIERS
        if group_set.intersection(s.groups) and s.code not in result
    ]
    extras.sort(key=lambda s: (0 if s.code in scrapable else 1, s.code))
    for supplier in extras:
        result.append(supplier.code)
        if len(result) >= limit:
            break
    return result[:limit]


def resolve_sources_for_item(
    category: str,
    *,
    available: set[str] | None = None,
    max_sources: int = 12,
) -> list[str]:
    """
    Combina retalhistas da categoria + marketplaces locais.
    Jumia/Jiji ficam no fim (lentos / falham com frequência).
    """
    preferred: list[str] = []
    # 1) Lojas da categoria (scrapáveis primeiro)
    for code in codes_for_catalog_category(category, limit=8):
        if code not in preferred:
            preferred.append(code)
    # 2) Marketplaces locais / regionais
    for code in ("kikolo", "socia", "praca_digital"):
        if code not in preferred:
            preferred.append(code)
    # 3) Remotos por último
    for code in ("jumia", "jiji"):
        if code not in preferred:
            preferred.append(code)

    if available is None:
        return preferred[:max_sources]
    return [c for c in preferred if c in available][:max_sources]
