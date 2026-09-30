-- Fontes adicionais para ingestão automática multi-setor

INSERT INTO public.scraping_sources (code, name, base_url, is_active) VALUES
    ('kikolo', 'Kikolo Online', 'https://kikoloonline.com', TRUE),
    ('socia', 'Socia.ao', 'https://socia.ao', TRUE),
    ('facebook_marketplace', 'Facebook Marketplace', 'https://www.facebook.com/marketplace', TRUE),
    ('praca_digital', 'Praça Digital', 'https://pracadigital.ao', TRUE)
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    base_url = EXCLUDED.base_url,
    is_active = TRUE;

-- Garantir jumia/jiji activos
UPDATE public.scraping_sources
SET is_active = TRUE
WHERE code IN ('jumia', 'jiji');
