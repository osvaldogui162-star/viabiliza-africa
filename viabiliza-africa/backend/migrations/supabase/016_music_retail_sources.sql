-- GudeSom e lojas de música / áudio (sector AO)
INSERT INTO public.scraping_sources (code, name, base_url, is_active, categories, scrape_enabled, city_note)
VALUES
    ('gudesom', 'GudeSom Angola', 'https://gudesom.com', TRUE, ARRAY['music','electrical'], TRUE, 'Viana / Av. Comandante Valódia'),
    ('iscotec_music', 'Iscotec Music', 'https://www.iscotec.co.ao', TRUE, ARRAY['music'], FALSE, 'Luanda'),
    ('vens_music', 'VENS Music', 'https://www.vensmusic.co.ao', TRUE, ARRAY['music'], FALSE, 'Luanda'),
    ('musicomania', 'Musicomania', 'https://www.musicomania.co.ao', TRUE, ARRAY['music'], FALSE, 'Bungo / Luanda'),
    ('king_kong_music', 'King Kong Music', 'https://www.kingkongmusic.co.ao', TRUE, ARRAY['music','appliances'], FALSE, 'Luanda'),
    ('casa_musica_ao', 'Casa da Música Angola', 'https://www.casadamusica.co.ao', TRUE, ARRAY['music'], FALSE, 'Luanda')
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    base_url = EXCLUDED.base_url,
    is_active = EXCLUDED.is_active,
    categories = EXCLUDED.categories,
    scrape_enabled = EXCLUDED.scrape_enabled,
    city_note = EXCLUDED.city_note;
