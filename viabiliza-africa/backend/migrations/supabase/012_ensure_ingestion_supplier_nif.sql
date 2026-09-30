-- Diagnóstico + garantia do Módulo 3 (cost_items + supplier_nif)
-- Corre no SQL Editor do MESMO projecto que a app usa (rfrqhwlrdkfjkruklyuh).
-- Não volta a criar policies/tabelas já existentes de forma destrutiva.

DO $$
DECLARE
    projects_id_type text;
BEGIN
    IF to_regclass('public.projects') IS NULL THEN
        RAISE EXCEPTION
            'A tabela public.projects não existe. Execute 001_module1_auth.sql e 002_module2_projects.sql primeiro.';
    END IF;

    SELECT c.data_type
      INTO projects_id_type
      FROM information_schema.columns c
     WHERE c.table_schema = 'public'
       AND c.table_name = 'projects'
       AND c.column_name = 'id';

    IF projects_id_type IS DISTINCT FROM 'uuid' THEN
        RAISE EXCEPTION
            'Incompatível: public.projects.id é "%" (esperado uuid). '
            'Isto acontece quando existe uma tabela projects antiga (integer). '
            'Soluções: (1) confirme que o SQL Editor está no projecto certo da app; '
            '(2) se for um projecto novo/errado, use o projecto onde a app já corre; '
            '(3) se quiser recriar este schema do zero, faça backup e apague as tabelas antigas antes de correr 001→011.',
            projects_id_type;
    END IF;

    IF to_regclass('public.users') IS NULL THEN
        RAISE EXCEPTION 'A tabela public.users não existe. Execute 001_module1_auth.sql primeiro.';
    END IF;
END $$;

-- cost_items (só cria se ainda não existir)
CREATE TABLE IF NOT EXISTS public.cost_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    item_type       VARCHAR(10) NOT NULL CHECK (item_type IN ('opex', 'capex')),
    category        VARCHAR(100) NOT NULL,
    description     TEXT NOT NULL,
    quantity        NUMERIC(14, 4) NOT NULL DEFAULT 1 CHECK (quantity > 0),
    unit            VARCHAR(30) NOT NULL DEFAULT 'un',
    unit_price      NUMERIC(18, 2) NOT NULL CHECK (unit_price >= 0),
    total_amount    NUMERIC(18, 2) NOT NULL CHECK (total_amount >= 0),
    currency        VARCHAR(5) NOT NULL,
    source          VARCHAR(20) NOT NULL DEFAULT 'manual'
                    CHECK (source IN ('manual', 'excel', 'scraping')),
    data_hash       VARCHAR(64) NOT NULL,
    supplier_name   VARCHAR(200),
    supplier_nif    VARCHAR(50),
    supplier_url    TEXT,
    scraping_result_id UUID,
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_by      UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Se a tabela já existia sem NIF, adiciona a coluna
ALTER TABLE public.cost_items
    ADD COLUMN IF NOT EXISTS supplier_nif VARCHAR(50);

CREATE INDEX IF NOT EXISTS idx_cost_items_project ON public.cost_items (project_id);
CREATE INDEX IF NOT EXISTS idx_cost_items_hash ON public.cost_items (data_hash);
CREATE INDEX IF NOT EXISTS idx_cost_items_type ON public.cost_items (item_type);
CREATE INDEX IF NOT EXISTS idx_cost_items_supplier_nif
    ON public.cost_items (supplier_nif)
    WHERE supplier_nif IS NOT NULL;

-- Confirmação
SELECT
    'ok' AS status,
    (SELECT data_type FROM information_schema.columns
      WHERE table_schema='public' AND table_name='projects' AND column_name='id') AS projects_id_type,
    EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public' AND table_name='cost_items' AND column_name='supplier_nif'
    ) AS has_supplier_nif;
