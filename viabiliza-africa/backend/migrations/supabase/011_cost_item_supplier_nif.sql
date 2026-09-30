-- NIF do fornecedor nos itens de custo (consulta AGT)
-- Pré-requisito: public.projects.id e public.cost_items com tipos UUID
-- Preferir 012_ensure_ingestion_supplier_nif.sql se 003 falhar por tipos incompatíveis.

DO $$
DECLARE
    projects_id_type text;
BEGIN
    IF to_regclass('public.projects') IS NULL THEN
        RAISE EXCEPTION
            'A tabela public.projects não existe. Execute 001 e 002 primeiro.';
    END IF;

    SELECT c.data_type INTO projects_id_type
      FROM information_schema.columns c
     WHERE c.table_schema = 'public'
       AND c.table_name = 'projects'
       AND c.column_name = 'id';

    IF projects_id_type IS DISTINCT FROM 'uuid' THEN
        RAISE EXCEPTION
            'public.projects.id é "%" (esperado uuid). '
            'Não execute 003/011 neste schema antigo. '
            'Use o projecto da app (UUID) ou a migration 012_ensure_ingestion_supplier_nif.sql.',
            projects_id_type;
    END IF;

    IF to_regclass('public.cost_items') IS NULL THEN
        RAISE EXCEPTION
            'A tabela public.cost_items não existe. '
            'Execute 003_module3_ingestion.sql ou 012_ensure_ingestion_supplier_nif.sql.';
    END IF;
END $$;

ALTER TABLE public.cost_items
    ADD COLUMN IF NOT EXISTS supplier_nif VARCHAR(50);

CREATE INDEX IF NOT EXISTS idx_cost_items_supplier_nif
    ON public.cost_items (supplier_nif)
    WHERE supplier_nif IS NOT NULL;
