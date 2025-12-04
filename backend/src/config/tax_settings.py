"""
Tax settings and default values for different regions/contexts
Focado no contexto de Angola (AGT - Administração Geral Tributária)
"""

# Configurações Fiscais de Angola
ANGOLA_TAX_SETTINGS = {
    'name': 'Angola',
    'currency': 'AOA',
    'taxes': {
        'iva': 14.0,  # Imposto sobre Valor Acrescentado (Regime Geral)
        'imposto_industrial': 25.0,  # Taxa geral
        'imposto_industrial_agricola': 10.0, # Setor Agrícola
        'inss_patronal': 8.0,  # Segurança Social (Empresa)
        'inss_trabalhador': 3.0,  # Segurança Social (Trabalhador)
        'amortizacao_imaterial': 25.0, # Taxa média para ativos intangíveis
    },
    # Taxas de depreciação anual (Vida útil = 100 / taxa)
    # Baseado nas tabelas de reintegração e amortização da AGT
    'depreciation_rates': { 
        'edificios_escritorios': 4.0, # 25 anos
        'edificios_industriais': 4.0, # 25 anos
        'obras_publicas': 4.0, # 25 anos
        'mobiliario': 10.0, # 10 anos
        'equipamento_informatico': 25.0, # 4 anos
        'software': 33.33, # 3 anos
        'equipamento_transporte_ligeiro': 25.0, # 4 anos
        'equipamento_transporte_pesado': 20.0, # 5 anos
        'maquinaria_industrial': 12.5, # 8 anos
        'ferramentas': 25.0, # 4 anos
        'equipamento_basico': 10.0, # 10 anos
    },
    'depreciation_years': { # Conversão para anos (arredondado)
        'edificios': 25,
        'viaturas': 4,
        'informatica': 4,
        'mobiliario': 10,
        'maquinaria': 8,
        'ferramentas': 4,
        'software': 3
    }
}

def get_tax_settings(context='ANGOLA'):
    """
    Get tax settings for a specific context
    """
    if context.upper() == 'ANGOLA':
        return ANGOLA_TAX_SETTINGS
    return ANGOLA_TAX_SETTINGS  # Default to Angola for now
