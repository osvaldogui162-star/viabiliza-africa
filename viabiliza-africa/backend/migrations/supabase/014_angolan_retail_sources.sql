-- Fontes de retalho angolano para ingestão automática de preços
-- Categorias / grupos em TEXT[] para encaminhar pesquisas por tipo de item

ALTER TABLE public.scraping_sources
    ALTER COLUMN code TYPE VARCHAR(50);

ALTER TABLE public.scraping_results
    ALTER COLUMN source TYPE VARCHAR(50);

ALTER TABLE public.scraping_sources
    ADD COLUMN IF NOT EXISTS categories TEXT[] NOT NULL DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS scrape_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS city_note TEXT;

-- Supermercados / retalho
INSERT INTO public.scraping_sources (code, name, base_url, is_active, categories, scrape_enabled, city_note) VALUES
    ('candando', 'Candando Viana', 'https://www.candando.co.ao', TRUE, ARRAY['supermarket'], FALSE, 'Viana'),
    ('angomart', 'AngoMart', 'https://www.angomart.co.ao', TRUE, ARRAY['supermarket','appliances'], FALSE, NULL),
    ('maxi', 'Maxi Supermarket', 'https://www.maxi.co.ao', TRUE, ARRAY['supermarket'], TRUE, NULL),
    ('shoprite', 'Shoprite Angola', 'https://shoprite.co.ao', TRUE, ARRAY['supermarket'], TRUE, NULL),
    ('nosso_super', 'Nosso Super', 'https://www.nossosuper.co.ao', TRUE, ARRAY['supermarket'], FALSE, NULL),
    ('fresmart', 'Fresmart', 'https://www.fresmart.co.ao', TRUE, ARRAY['supermarket'], FALSE, NULL),
    ('martal', 'Martal', 'https://www.martal.co.ao', TRUE, ARRAY['supermarket'], FALSE, NULL),
    ('alimenta_ao', 'Alimenta Angola', 'https://www.alimentaangola.co.ao', TRUE, ARRAY['supermarket'], FALSE, NULL),
    ('intermarket', 'Intermarket', 'https://www.intermarket.co.ao', TRUE, ARRAY['supermarket'], FALSE, NULL),
    ('megamart', 'Megamart', 'https://www.megamart.co.ao', TRUE, ARRAY['supermarket'], FALSE, NULL),
    ('nossa_casa', 'Nossa Casa', 'https://www.nossacasa.co.ao', TRUE, ARRAY['supermarket','furniture'], FALSE, NULL),
    ('bompreco', 'Bompreço', 'https://www.bompreco.co.ao', TRUE, ARRAY['supermarket'], FALSE, NULL),
    ('continente_ao', 'Continente Angola', 'https://www.continente.co.ao', TRUE, ARRAY['supermarket'], FALSE, NULL),
    ('ok_super', 'OK Supermercados', 'https://www.ok.co.ao', TRUE, ARRAY['supermarket'], FALSE, NULL),
    ('usave', 'Usave', 'https://www.usave.co.ao', TRUE, ARRAY['supermarket'], FALSE, NULL),
    ('casa_frescos', 'Casa dos Frescos', 'https://www.casadosfrescos.co.ao', TRUE, ARRAY['supermarket'], FALSE, NULL),
-- Construção
    ('bricomat', 'Bricomat Mutamba', 'https://www.bricomat.co.ao', TRUE, ARRAY['construction','plumbing','electrical','epi'], TRUE, 'Mutamba'),
    ('ovarmat', 'Ovarmat Angola', 'https://www.ovarmatangola.com', TRUE, ARRAY['construction','plumbing','epi'], TRUE, 'Viana / Benfica'),
    ('dama', 'Dama', 'https://www.dama.co.ao', TRUE, ARRAY['construction','plumbing','furniture'], FALSE, NULL),
    ('intercal', 'Intercal', 'https://www.intercal.co.ao', TRUE, ARRAY['construction','electrical','epi','plumbing'], TRUE, NULL),
    ('o_index', 'O-Index', 'https://www.o-index.co.ao', TRUE, ARRAY['construction','electrical','epi','plumbing'], TRUE, NULL),
    ('ferro_lundas', 'Ferro-Lundas', 'https://www.ferrolundas.co.ao', TRUE, ARRAY['construction','epi'], TRUE, NULL),
    ('nour', 'Nour Company', 'https://www.nourcompany.co.ao', TRUE, ARRAY['construction'], FALSE, NULL),
    ('fouress', 'Fouress Group', 'https://www.fouress.co.ao', TRUE, ARRAY['construction'], FALSE, NULL),
-- Elétrico
    ('siluz', 'SILUZ Angola', 'https://siluzangola.com', TRUE, ARRAY['electrical'], TRUE, 'São Paulo / Viana'),
    ('soletric', 'Soletric', 'https://www.soletric.co.ao', TRUE, ARRAY['electrical','epi'], TRUE, NULL),
-- IT
    ('ncr', 'NCR Angola', 'https://www.ncrangola.com', TRUE, ARRAY['it','appliances','stationery'], TRUE, 'Talatona / Luanda'),
    ('sistec', 'SISTEC Lojas', 'https://loja.sistec.co.ao', TRUE, ARRAY['it','appliances'], TRUE, 'Maculusso / rede nacional'),
    ('itec', 'ITEC LDA Alvalade', 'https://www.itec.co.ao', TRUE, ARRAY['it'], TRUE, 'Alvalade'),
    ('zicai', 'Zicai Grupo Infornet Viana', 'https://www.zicai.co.ao', TRUE, ARRAY['it'], FALSE, 'Viana'),
    ('megatech', 'Megatech', 'https://www.megatech.co.ao', TRUE, ARRAY['it','appliances'], TRUE, NULL),
    ('casa_pcs', 'Casa dos Computadores', 'https://www.casadoscomputadores.co.ao', TRUE, ARRAY['it'], TRUE, NULL),
-- Móveis
    ('moviflor', 'Moviflor Angola', 'https://moviflor.ao', TRUE, ARRAY['furniture'], TRUE, NULL),
    ('dama_home', 'Dama Home', 'https://www.damahome.co.ao', TRUE, ARRAY['furniture'], FALSE, NULL),
    ('casa_moveis', 'Casa dos Móveis', 'https://www.casadosmoveis.co.ao', TRUE, ARRAY['furniture'], FALSE, NULL),
    ('decor_ao', 'Decor Angola', 'https://www.decorangola.co.ao', TRUE, ARRAY['furniture'], FALSE, NULL),
    ('casa_design', 'Casa Design', 'https://www.casadesign.co.ao', TRUE, ARRAY['furniture'], FALSE, NULL),
-- Automóveis
    ('toyota_ao', 'Toyota Angola / CFAO', 'https://www.cfaomotorsangola.com', TRUE, ARRAY['auto','auto_parts'], TRUE, NULL),
    ('cfao', 'CFAO Mobility Angola', 'https://www.cfaomotorsangola.com', TRUE, ARRAY['auto','auto_parts'], FALSE, NULL),
    ('hyundai_ao', 'Hyundai Angola', 'https://www.hyundai.co.ao', TRUE, ARRAY['auto'], FALSE, NULL),
    ('nissan_ao', 'Nissan Angola', 'https://www.nissan.co.ao', TRUE, ARRAY['auto'], FALSE, NULL),
    ('kia_ao', 'Kia Angola', 'https://www.kia.co.ao', TRUE, ARRAY['auto'], FALSE, NULL),
    ('mercedes_ao', 'Mercedes-Benz Angola', 'https://www.mercedes-benz.co.ao', TRUE, ARRAY['auto'], FALSE, NULL),
    ('auto_sueco', 'Auto Sueco', 'https://www.autosueco.co.ao', TRUE, ARRAY['auto'], FALSE, NULL),
    ('renault_ao', 'Renault Angola', 'https://www.renault.co.ao', TRUE, ARRAY['auto'], FALSE, NULL),
    ('ford_ao', 'Ford Angola', 'https://www.ford.co.ao', TRUE, ARRAY['auto'], FALSE, NULL),
-- Peças auto
    ('auto_koka', 'Auto Koka', 'https://www.autokoka.co.ao', TRUE, ARRAY['auto_parts'], FALSE, NULL),
    ('auto_pecas_vn', 'Auto Peças Viana', 'https://www.autopecasviana.co.ao', TRUE, ARRAY['auto_parts'], FALSE, 'Viana'),
    ('casa_pecas', 'Casa das Peças', 'https://www.casadaspecas.co.ao', TRUE, ARRAY['auto_parts'], FALSE, NULL),
    ('lubriang', 'Lubriang', 'https://www.lubriang.co.ao', TRUE, ARRAY['auto_parts'], FALSE, NULL),
    ('auto_stop', 'Auto Stop', 'https://www.autostop.co.ao', TRUE, ARRAY['auto_parts'], FALSE, NULL),
-- Farmácias
    ('farm_central', 'Farmácia Central', 'https://www.farmaciacentral.co.ao', TRUE, ARRAY['pharmacy'], FALSE, NULL),
    ('farm_popular', 'Farmácia Popular', 'https://www.farmaciapopular.co.ao', TRUE, ARRAY['pharmacy'], FALSE, NULL),
    ('farm_cristal', 'Farmácia Cristal', 'https://www.farmaciacristal.co.ao', TRUE, ARRAY['pharmacy'], FALSE, NULL),
    ('farm_universal', 'Farmácia Universal', 'https://www.farmaciauniversal.co.ao', TRUE, ARRAY['pharmacy'], FALSE, NULL),
    ('farm_kianda', 'Farmácia Kianda', 'https://www.farmaciakianda.co.ao', TRUE, ARRAY['pharmacy'], FALSE, NULL),
    ('farm_nacional', 'Farmácia Nacional', 'https://www.farmacianacional.co.ao', TRUE, ARRAY['pharmacy'], FALSE, NULL),
-- Eletrodomésticos
    ('arreiou', 'Arreiou', 'https://arreiou.com', TRUE, ARRAY['appliances','supermarket'], TRUE, NULL),
    ('bestmarket', 'Bestmarket', 'https://www.bestmarket.co.ao', TRUE, ARRAY['appliances'], FALSE, NULL),
    ('casa_eletros', 'Casa dos Eletrodomésticos', 'https://www.casadoseletrodomesticos.co.ao', TRUE, ARRAY['appliances'], FALSE, NULL),
    ('megastore', 'Megastore', 'https://www.megastore.co.ao', TRUE, ARRAY['appliances'], FALSE, NULL),
-- Papelarias
    ('escolar_ed', 'Livraria Escolar Editora', 'https://www.escolareditora.co.ao', TRUE, ARRAY['stationery'], TRUE, NULL),
    ('papel_univ', 'Papelaria Universal', 'https://www.papelariauniversal.co.ao', TRUE, ARRAY['stationery'], FALSE, NULL),
    ('papel_nova', 'Papelaria Nova', 'https://www.papelarianova.co.ao', TRUE, ARRAY['stationery'], FALSE, NULL),
-- Agricultura
    ('naval', 'Naval', 'https://www.naval.co.ao', TRUE, ARRAY['agriculture'], TRUE, NULL),
    ('agrolider', 'Agrolíder', 'https://www.agrolider.co.ao', TRUE, ARRAY['agriculture'], TRUE, NULL),
    ('agrocampo', 'AgroCampo', 'https://www.agrocampo.co.ao', TRUE, ARRAY['agriculture'], FALSE, NULL),
    ('agroshop', 'Agroshop Angola', 'https://www.agroshop.co.ao', TRUE, ARRAY['agriculture'], TRUE, NULL)
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    base_url = EXCLUDED.base_url,
    is_active = TRUE,
    categories = EXCLUDED.categories,
    scrape_enabled = EXCLUDED.scrape_enabled,
    city_note = EXCLUDED.city_note;

-- Actualizar marketplaces existentes com categorias
UPDATE public.scraping_sources
SET categories = ARRAY['marketplace'], scrape_enabled = TRUE
WHERE code IN ('jumia', 'jiji', 'kikolo', 'socia', 'praca_digital', 'facebook_marketplace');
