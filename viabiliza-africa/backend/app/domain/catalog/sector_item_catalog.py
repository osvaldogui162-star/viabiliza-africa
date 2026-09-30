"""Catálogo de itens típicos por setor para ingestão automática."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.domain.enums.cost_item_type import CostItemType
from app.domain.enums.project_sector import ProjectSector
from app.domain.catalog.sector_modules import SectorModuleRegistry


@dataclass(frozen=True)
class CatalogItem:
    """Item necessário para um projecto de viabilidade no setor."""

    key: str
    item_type: str  # capex | opex
    category: str
    description: str
    quantity: Decimal
    unit: str
    search_query: str
    """Consulta para marketplaces (bens materiais)."""
    pricing_mode: str = "scrape"
    """scrape | hybrid | reference — reference usa preço de referência setorial."""
    reference_price: Decimal | None = None
    """Preço de referência AOA quando scrape não encontrar (serviços/mão-de-obra)."""
    reference_note: str | None = None


def _i(
    key: str,
    item_type: str,
    category: str,
    description: str,
    quantity: str | float | int,
    unit: str,
    search_query: str,
    *,
    pricing_mode: str = "scrape",
    reference_price: str | float | int | None = None,
    reference_note: str | None = None,
) -> CatalogItem:
    return CatalogItem(
        key=key,
        item_type=item_type,
        category=category,
        description=description,
        quantity=Decimal(str(quantity)),
        unit=unit,
        search_query=search_query,
        pricing_mode=pricing_mode,
        reference_price=Decimal(str(reference_price)) if reference_price is not None else None,
        reference_note=reference_note,
    )


# Itens transversais a quase todos os projectos
_COMMON: list[CatalogItem] = [
    _i("doc_licencas", "capex", "Documentação", "Licenças e registos (GUE/AGT/actividade)", 1, "un",
       "taxa licença empresa", pricing_mode="reference", reference_price="250000",
       reference_note="Estimativa administrativa GUE/AGT"),
    _i("doc_estudo", "capex", "Documentação", "Elaboração de estudo de viabilidade / diligências", 1, "un",
       "consultoria estudo viabilidade", pricing_mode="reference", reference_price="1500000",
       reference_note="Referência mercado consultoria AO"),
    _i("it_computador", "capex", "IT", "Computador portátil / posto de trabalho", 2, "un",
       "computador portátil"),
    _i("it_impressora", "capex", "IT", "Impressora multifunções", 1, "un",
       "impressora multifunções"),
    _i("movel_escritorio", "capex", "Mobiliário", "Mobiliário de escritório (mesa + cadeiras)", 1, "lote",
       "mesa escritório cadeira"),
    _i("opex_internet", "opex", "Telecom", "Internet / comunicações (anual)", 12, "mês",
       "internet fibra casa"),
    _i("opex_contabilidade", "opex", "Serviços", "Contabilidade e compliance fiscal (anual)", 12, "mês",
       "contabilidade empresa", pricing_mode="hybrid", reference_price="150000",
       reference_note="Honorário mensal típico contabilista AO"),
]


_SECTOR: dict[str, list[CatalogItem]] = {
    ProjectSector.AGRICULTURE.value: [
        _i("ag_trator", "capex", "Equipamento", "Tractor agrícola / motocultivador", 1, "un", "tractor agrícola"),
        _i("ag_bomba", "capex", "Equipamento", "Sistema de irrigação / bomba de água", 1, "un", "bomba água irrigação"),
        _i("ag_gerador", "capex", "Equipamento", "Gerador diesel para campo", 1, "un", "gerador diesel"),
        _i("ag_armazem", "capex", "Infraestrutura", "Estrutura de armazém / silo básico", 1, "un", "estrutura metálica armazém"),
        _i("ag_sementes", "opex", "Insumos", "Sementes e adubos (campanha anual)", 1, "lote", "adubo sementes"),
        _i("ag_combustivel", "opex", "Energia", "Combustível operações anuais", 12, "mês", "gasóleo combustível"),
        _i("ag_agronomo", "opex", "Pessoal", "Engenheiro agrónomo (honorários anuais)", 12, "mês",
           "engenheiro agrónomo", pricing_mode="hybrid", reference_price="450000",
           reference_note="Honorário mensal Eng. Agrónomo — referência mercado AO"),
        _i("ag_operarios", "opex", "Pessoal", "Operários agrícolas (salários anuais)", 12, "mês",
           "salário operário agrícola", pricing_mode="reference", reference_price="120000",
           reference_note="SMN/salário médio operário rural AO × equipa"),
    ],
    ProjectSector.MANUFACTURING.value: [
        _i("mfg_linha", "capex", "Equipamento", "Linha / máquina de produção", 1, "un", "máquina industrial"),
        _i("mfg_gerador", "capex", "Energia", "Gerador industrial", 1, "un", "gerador industrial"),
        _i("mfg_empilhador", "capex", "Logística", "Empilhador / movimentação", 1, "un", "empilhador"),
        _i("mfg_epi", "capex", "Segurança", "EPIs e segurança industrial", 1, "lote", "capacete segurança EPI"),
        _i("mfg_mp", "opex", "Matérias-primas", "Matérias-primas anuais", 12, "mês", "matéria prima industrial"),
        _i("mfg_energia", "opex", "Energia", "Energia eléctrica industrial (anual)", 12, "mês", "energia eléctrica"),
        _i("mfg_eng", "opex", "Pessoal", "Engenheiro de produção (anual)", 12, "mês",
           "engenheiro industrial", pricing_mode="hybrid", reference_price="550000",
           reference_note="Honorário/salário Eng. Produção AO"),
        _i("mfg_ops", "opex", "Pessoal", "Operadores de linha (anual)", 12, "mês",
           "operador fábrica", pricing_mode="reference", reference_price="180000",
           reference_note="Salário médio operador industrial AO"),
    ],
    ProjectSector.CONSTRUCTION.value: [
        _i("cst_betoneira", "capex", "Equipamento", "Betoneira / equipamentos de obra", 1, "un", "betoneira"),
        _i("cst_andaimes", "capex", "Equipamento", "Andaimes e ferramentas", 1, "lote", "andaime construção"),
        _i("cst_cimento", "opex", "Materiais", "Cimento e agregados (fase obra)", 100, "saco", "cimento"),
        _i("cst_ferro", "opex", "Materiais", "Ferro / aço de construção", 1, "lote", "ferro construção"),
        _i("cst_tijolo", "opex", "Materiais", "Tijolos / blocos", 1000, "un", "bloco tijolo"),
        _i("cst_eng", "opex", "Pessoal", "Engenheiro civil (honorários obra)", 12, "mês",
           "engenheiro civil", pricing_mode="hybrid", reference_price="600000",
           reference_note="Honorário Eng. Civil AO"),
        _i("cst_mestres", "opex", "Pessoal", "Mestres de obra e pedreiros", 12, "mês",
           "pedreiro salário", pricing_mode="reference", reference_price="200000",
           reference_note="Salário mestre/pedreiro AO"),
    ],
    ProjectSector.ENERGY.value: [
        _i("en_paineis", "capex", "Equipamento", "Painéis solares / kit FV", 1, "lote", "painel solar"),
        _i("en_inversor", "capex", "Equipamento", "Inversor e baterias", 1, "lote", "inversor solar bateria"),
        _i("en_gerador", "capex", "Equipamento", "Gerador de apoio", 1, "un", "gerador diesel"),
        _i("en_cablagem", "capex", "Materiais", "Cablagem e estrutura de montagem", 1, "lote", "cabo eléctrico"),
        _i("en_manut", "opex", "Manutenção", "Manutenção anual do sistema", 1, "un", "manutenção painel solar"),
        _i("en_tec", "opex", "Pessoal", "Técnico de energia (anual)", 12, "mês",
           "técnico electricista", pricing_mode="hybrid", reference_price="350000",
           reference_note="Técnico electricista/energia AO"),
    ],
    ProjectSector.TECHNOLOGY.value: [
        _i("tech_servidores", "capex", "IT", "Servidores / cloud on-prem", 1, "lote", "servidor computador"),
        _i("tech_rede", "capex", "IT", "Rede, routers e segurança", 1, "lote", "router switch rede"),
        _i("tech_licencas", "capex", "Software", "Licenças de software", 1, "lote", "licença software",
           pricing_mode="hybrid", reference_price="800000", reference_note="Pacote licenças SaaS/ano"),
        _i("tech_dev", "opex", "Pessoal", "Equipa de desenvolvimento (anual)", 12, "mês",
           "programador salário", pricing_mode="hybrid", reference_price="500000",
           reference_note="Dev full-stack médio AO"),
        _i("tech_cloud", "opex", "Infraestrutura", "Hosting / cloud anual", 12, "mês", "hosting cloud"),
        _i("tech_suporte", "opex", "Serviços", "Suporte e manutenção de sistemas", 12, "mês",
           "suporte informático", pricing_mode="reference", reference_price="200000",
           reference_note="Contrato suporte IT mensal"),
    ],
    ProjectSector.HEALTH.value: [
        _i("hl_equip", "capex", "Equipamento", "Equipamento clínico básico", 1, "lote", "equipamento médico"),
        _i("hl_mobiliario", "capex", "Mobiliário", "Mobiliário clínico", 1, "lote", "maca consultório"),
        _i("hl_frio", "capex", "Equipamento", "Câmara fria / refrigeração medicamentos", 1, "un", "frigorífico"),
        _i("hl_consumiveis", "opex", "Consumíveis", "Consumíveis clínicos anuais", 12, "mês", "máscara luvas hospitalar"),
        _i("hl_medico", "opex", "Pessoal", "Médico / clínico (anual)", 12, "mês",
           "médico salário", pricing_mode="reference", reference_price="800000",
           reference_note="Honorário médico AO"),
        _i("hl_enfermeiro", "opex", "Pessoal", "Enfermagem (anual)", 12, "mês",
           "enfermeiro salário", pricing_mode="reference", reference_price="350000",
           reference_note="Salário enfermagem AO"),
    ],
    ProjectSector.EDUCATION.value: [
        _i("ed_salas", "capex", "Infraestrutura", "Mobiliário de salas de aula", 1, "lote", "carteira escolar"),
        _i("ed_quadro", "capex", "Equipamento", "Quadros e projectores", 2, "un", "projector"),
        _i("ed_biblioteca", "capex", "Material", "Livros e material didáctico", 1, "lote", "livro escolar"),
        _i("ed_pc", "capex", "IT", "Laboratório de informática", 10, "un", "computador desktop"),
        _i("ed_prof", "opex", "Pessoal", "Professores (anual)", 12, "mês",
           "professor salário", pricing_mode="reference", reference_price="250000",
           reference_note="Salário professor AO"),
        _i("ed_admin", "opex", "Pessoal", "Administração escolar (anual)", 12, "mês",
           "secretário escolar", pricing_mode="reference", reference_price="180000",
           reference_note="Administrativo escolar AO"),
    ],
    ProjectSector.TOURISM.value: [
        _i("tu_mobilia", "capex", "Mobiliário", "Mobiliário hoteleiro / alojamento", 1, "lote", "cama hotel colchão"),
        _i("tu_cozinha", "capex", "Equipamento", "Equipamento de cozinha industrial", 1, "lote", "fogão industrial"),
        _i("tu_lavandaria", "capex", "Equipamento", "Lavandaria", 1, "lote", "máquina lavar roupa"),
        _i("tu_decoracao", "capex", "Ambientação", "Decoração e amenities", 1, "lote", "decoração casa"),
        _i("tu_som", "capex", "Áudio", "Sistema de som / PA para eventos e bar", 1, "lote", "mesa de som coluna PA"),
        _i("tu_microfones", "capex", "Áudio", "Microfones e acessórios de palco", 4, "un", "microfone profissional"),
        _i("tu_luz", "capex", "Eventos", "Iluminação cénica / box truss", 1, "lote", "iluminação led eventos"),
        _i("tu_alimentos", "opex", "F&B", "Alimentos e bebidas (anual)", 12, "mês", "arroz óleo farinha"),
        _i("tu_staff", "opex", "Pessoal", "Recepcionistas e limpeza (anual)", 12, "mês",
           "recepcionista hotel", pricing_mode="reference", reference_price="150000",
           reference_note="Staff hotelaria AO"),
    ],
    ProjectSector.RETAIL.value: [
        _i("rt_prateleiras", "capex", "Mobiliário", "Prateleiras e expositores", 1, "lote", "prateleira loja"),
        _i("rt_pos", "capex", "IT", "POS / caixa e software", 2, "un", "pos caixa registadora"),
        _i("rt_frigorifico", "capex", "Equipamento", "Expositores refrigerados", 1, "un", "frigorífico expositor"),
        _i("rt_stock", "opex", "Stock", "Stock inicial de mercadoria", 1, "lote", "produtos supermercado"),
        _i("rt_vendedor", "opex", "Pessoal", "Vendedores (anual)", 12, "mês",
           "vendedor loja", pricing_mode="reference", reference_price="140000",
           reference_note="Salário vendedor retalho AO"),
    ],
    ProjectSector.TRANSPORT.value: [
        _i("tr_veiculo", "capex", "Frota", "Veículo comercial / camião ligeiro", 1, "un", "camião pickup"),
        _i("tr_pneus", "capex", "Manutenção", "Pneus e peças iniciais", 1, "lote", "pneu camião"),
        _i("tr_gps", "capex", "IT", "Rastreio GPS frota", 1, "lote", "gps tracker veículo"),
        _i("tr_combustivel", "opex", "Energia", "Combustível anual", 12, "mês", "gasóleo"),
        _i("tr_motorista", "opex", "Pessoal", "Motoristas (anual)", 12, "mês",
           "motorista salário", pricing_mode="reference", reference_price="200000",
           reference_note="Salário motorista AO"),
        _i("tr_seguro", "opex", "Seguros", "Seguro frota anual", 1, "un",
           "seguro automóvel", pricing_mode="hybrid", reference_price="350000",
           reference_note="Prémio seguro veículo comercial"),
    ],
    ProjectSector.MINING.value: [
        _i("mn_perfuracao", "capex", "Equipamento", "Equipamento de perfuração / extracção", 1, "un", "máquina perfuração"),
        _i("mn_epi", "capex", "Segurança", "EPIs mineração", 1, "lote", "capacete segurança botas"),
        _i("mn_gerador", "capex", "Energia", "Gerador de campo", 1, "un", "gerador diesel"),
        _i("mn_transporte", "capex", "Logística", "Veículo de transporte de minério", 1, "un", "camião basculante"),
        _i("mn_geologo", "opex", "Pessoal", "Geólogo / técnico de mina", 12, "mês",
           "geólogo", pricing_mode="reference", reference_price="700000",
           reference_note="Honorário geólogo AO"),
        _i("mn_ops", "opex", "Pessoal", "Operadores de máquina", 12, "mês",
           "operador máquina", pricing_mode="reference", reference_price="250000",
           reference_note="Operador equipamentos pesados"),
    ],
    ProjectSector.REAL_ESTATE.value: [
        _i("re_terreno", "capex", "Imóvel", "Aquisição / direitos de terreno (estudo)", 1, "un",
           "terreno venda luanda", pricing_mode="hybrid", reference_price="15000000",
           reference_note="Referência parcelar — validar com mercado local"),
        _i("re_projecto", "capex", "Documentação", "Projecto arquitectónico", 1, "un",
           "projecto arquitectura", pricing_mode="reference", reference_price="2500000",
           reference_note="Honorário arquitectura AO"),
        _i("re_materiais", "opex", "Materiais", "Materiais de construção (fase)", 1, "lote", "cimento ferro tijolo"),
        _i("re_mestre", "opex", "Pessoal", "Mestre de obras", 12, "mês",
           "mestre obra", pricing_mode="reference", reference_price="300000",
           reference_note="Mestre de obras AO"),
    ],
    ProjectSector.SERVICES.value: [
        _i("sv_escritorio", "capex", "Infraestrutura", "Montagem de escritório", 1, "lote", "mobiliário escritório"),
        _i("sv_software", "capex", "Software", "Software de gestão", 1, "un", "software gestão empresa"),
        _i("sv_audio", "capex", "Áudio", "Equipamento de som para apresentações", 1, "lote", "coluna amplificador microfone"),
        _i("sv_marketing", "opex", "Marketing", "Marketing e aquisição de clientes", 12, "mês", "marketing digital"),
        _i("sv_consultor", "opex", "Pessoal", "Consultores / especialistas", 12, "mês",
           "consultor salário", pricing_mode="hybrid", reference_price="400000",
           reference_note="Consultor independente AO"),
        _i("sv_admin", "opex", "Pessoal", "Assistente administrativo", 12, "mês",
           "assistente administrativo", pricing_mode="reference", reference_price="160000",
           reference_note="Administrativo AO"),
    ],
    ProjectSector.OTHER.value: [
        _i("ot_equip", "capex", "Equipamento", "Equipamento operacional principal", 1, "un", "equipamento"),
        _i("ot_setup", "capex", "Arranque", "Custos de arranque e instalação", 1, "lote", "ferramentas"),
        _i("ot_som", "capex", "Áudio", "Instrumentos / som (se sector musical)", 1, "lote", "guitarra teclado mesa de som"),
        _i("ot_ops", "opex", "Operação", "Custos operacionais anuais", 12, "mês", "material escritório"),
        _i("ot_pessoal", "opex", "Pessoal", "Equipa operacional", 12, "mês",
           "salário funcionário", pricing_mode="reference", reference_price="180000",
           reference_note="Salário médio trabalhador AO"),
    ],
}

# Itens adicionais por módulo setorial (UC60–UC100) — orientam ingestão sem substituir o catálogo base
_MODULE_EXTRAS: dict[str, list[CatalogItem]] = {
    "agri_tech": [
        _i("ag_solo", "capex", "Estudos", "Análise de solo e interpretação agronómica", 1, "un",
           "análise solo agrícola", pricing_mode="reference", reference_price="180000",
           reference_note="Laboratório agrícola — referência UC61"),
        _i("ag_sensores", "capex", "IoT", "Kit sensores campo (humidade/temperatura) — referência", 1, "lote",
           "sensor humidade solo", pricing_mode="hybrid", reference_price="450000",
           reference_note="Referência IoT agrícola UC60"),
        _i("ag_irrigacao", "capex", "Infraestrutura", "Estudo / projecto de irrigação por gotejamento", 1, "un",
           "irrigação gotejamento", pricing_mode="reference", reference_price="800000",
           reference_note="Projecto irrigação UC63"),
    ],
    "industry_40": [
        _i("mfg_oee", "capex", "Consultoria", "Diagnóstico OEE e produtividade industrial", 1, "un",
           "consultoria produtividade industrial", pricing_mode="reference", reference_price="1200000",
           reference_note="Auditoria OEE UC70"),
        _i("mfg_qualidade", "capex", "Qualidade", "Equipamento laboratório controlo qualidade", 1, "lote",
           "equipamento laboratório qualidade", pricing_mode="hybrid", reference_price="950000",
           reference_note="Controlo qualidade UC71"),
        _i("mfg_seguranca", "capex", "Segurança", "Auditoria segurança industrial / HAZOP", 1, "un",
           "auditoria segurança industrial", pricing_mode="reference", reference_price="650000",
           reference_note="Segurança industrial UC73"),
    ],
    "infrastructure": [
        _i("inf_lcoe", "capex", "Estudos", "Estudo de viabilidade solar / LCOE", 1, "un",
           "estudo energia solar", pricing_mode="reference", reference_price="900000",
           reference_note="Análise LCOE UC77"),
        _i("inf_rede", "capex", "Estudos", "Estudo de ligação à rede eléctrica", 1, "un",
           "ligação rede eléctrica", pricing_mode="reference", reference_price="550000",
           reference_note="Infraestrutura energética UC78"),
        _i("inf_ambiental", "capex", "Documentação", "Estudo de impacto ambiental (EIA)", 1, "un",
           "estudo impacto ambiental", pricing_mode="reference", reference_price="2500000",
           reference_note="Compliance ambiental UC79"),
    ],
    "mobility": [
        _i("mob_rota", "capex", "Software", "Software optimização rotas / TMS", 1, "un",
           "software gestão frota", pricing_mode="hybrid", reference_price="600000",
           reference_note="Optimização logística UC84"),
        _i("mob_armazem", "capex", "Logística", "Estanteria / picking armazém", 1, "lote",
           "estanteria armazém", pricing_mode="scrape"),
    ],
    "tourism": [
        _i("tu_pms", "capex", "Software", "PMS hoteleiro / gestão reservas", 1, "un",
           "software hotel PMS", pricing_mode="hybrid", reference_price="750000",
           reference_note="Gestão hoteleira UC89"),
        _i("tu_sustent", "capex", "Certificação", "Auditoria sustentabilidade / GSTC", 1, "un",
           "certificação turismo sustentável", pricing_mode="reference", reference_price="400000",
           reference_note="Certificação turística UC92"),
    ],
    "esg": [
        _i("esg_carbono", "capex", "ESG", "Inventário pegada de carbono (tCO2e)", 1, "un",
           "inventário carbono empresa", pricing_mode="reference", reference_price="350000",
           reference_note="Pegada carbono UC93"),
        _i("esg_governanca", "opex", "ESG", "Consultoria governança e compliance (anual)", 12, "mês",
           "consultoria governança", pricing_mode="reference", reference_price="280000",
           reference_note="Governança UC95"),
    ],
}


class SectorItemCatalog:
    """Fornece lista de itens necessários por setor de projecto."""

    def list_for_sector(self, sector: str) -> list[CatalogItem]:
        key = (sector or ProjectSector.OTHER.value).lower()
        if not ProjectSector.is_valid(key):
            key = ProjectSector.OTHER.value
        sector_items = list(_SECTOR.get(key, _SECTOR[ProjectSector.OTHER.value]))
        module_code = SectorModuleRegistry.primary_module_code(key)
        module_extras = list(_MODULE_EXTRAS.get(module_code, []))
        # ESG transversal — documentação de sustentabilidade
        module_extras.extend(_MODULE_EXTRAS.get("esg", []))
        existing_keys = {i.key for i in sector_items}
        for extra in module_extras:
            if extra.key not in existing_keys:
                sector_items.append(extra)
                existing_keys.add(extra.key)
        # Evitar duplicar IT/common se já coberto pelo setor
        sector_keys = {i.category for i in sector_items}
        extras = [
            c for c in _COMMON
            if c.category not in sector_keys or c.key.startswith("doc_")
        ]
        # Preferir itens do setor + documentação transversal
        docs = [c for c in _COMMON if c.key.startswith("doc_")]
        transversais = [c for c in _COMMON if not c.key.startswith("doc_")]
        # filtrar transversais que já existem por description similar
        combined = docs + sector_items
        existing_desc = {i.description.lower() for i in combined}
        for item in transversais:
            if item.description.lower() not in existing_desc:
                combined.append(item)
        return combined

    def to_preview(self, sector: str) -> list[dict]:
        return [
            {
                "key": i.key,
                "item_type": i.item_type,
                "category": i.category,
                "description": i.description,
                "quantity": format(i.quantity, "f"),
                "unit": i.unit,
                "search_query": i.search_query,
                "pricing_mode": i.pricing_mode,
                "has_reference_price": i.reference_price is not None,
            }
            for i in self.list_for_sector(sector)
        ]
