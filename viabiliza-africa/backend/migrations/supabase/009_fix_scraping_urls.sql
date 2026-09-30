-- Cria/actualiza fontes de scraping (autónomo — não depende de 003/008)

CREATE TABLE IF NOT EXISTS public.scraping_sources (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code        VARCHAR(30) NOT NULL UNIQUE,
    name        VARCHAR(100) NOT NULL,
    base_url    TEXT NOT NULL,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    description TEXT,
    country     VARCHAR(5) DEFAULT 'AO',
    config      JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by  UUID
);

-- Colunas extra (caso a tabela já exista na versão mínima do módulo 3)
ALTER TABLE public.scraping_sources
    ADD COLUMN IF NOT EXISTS description TEXT,
    ADD COLUMN IF NOT EXISTS country VARCHAR(5) DEFAULT 'AO',
    ADD COLUMN IF NOT EXISTS config JSONB NOT NULL DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS updated_by UUID;

INSERT INTO public.scraping_sources (code, name, base_url, is_active, country) VALUES
    ('jumia', 'Jumia Angola', 'https://www.jumia.ao', TRUE, 'AO'),
    ('jiji', 'Jiji Angola', 'https://jiji.ao', TRUE, 'AO')
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    base_url = EXCLUDED.base_url,
    is_active = TRUE,
    updated_at = NOW();

ALTER TABLE public.scraping_sources ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_scraping_sources" ON public.scraping_sources;
CREATE POLICY "service_role_scraping_sources"
    ON public.scraping_sources
    FOR ALL
    USING (true)
    WITH CHECK (true);
