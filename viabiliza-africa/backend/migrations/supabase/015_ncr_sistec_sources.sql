-- Actualiza NCR e SISTEC (scraping + grupos) se a 014 já tiver corrido.
INSERT INTO public.scraping_sources (code, name, base_url, is_active, categories, scrape_enabled, city_note)
VALUES
    ('ncr', 'NCR Angola', 'https://www.ncrangola.com', TRUE, ARRAY['it', 'appliances', 'stationery'], TRUE, 'Talatona / Luanda'),
    ('sistec', 'SISTEC Lojas', 'https://loja.sistec.co.ao', TRUE, ARRAY['it', 'appliances'], TRUE, 'Maculusso / rede nacional')
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    base_url = EXCLUDED.base_url,
    is_active = EXCLUDED.is_active,
    categories = EXCLUDED.categories,
    scrape_enabled = EXCLUDED.scrape_enabled,
    city_note = EXCLUDED.city_note;
