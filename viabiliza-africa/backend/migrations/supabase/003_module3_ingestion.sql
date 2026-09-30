-- ViabilizA+ África — Módulo 3: Ingestão de Dados Rastreável
-- Executar após 002_module2_projects.sql

-- ---------------------------------------------------------------------------
-- Itens OPEX/CAPEX
-- ---------------------------------------------------------------------------
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

CREATE INDEX IF NOT EXISTS idx_cost_items_project ON public.cost_items (project_id);
CREATE INDEX IF NOT EXISTS idx_cost_items_hash ON public.cost_items (data_hash);
CREATE INDEX IF NOT EXISTS idx_cost_items_type ON public.cost_items (item_type);

DROP TRIGGER IF EXISTS trg_cost_items_updated_at ON public.cost_items;
CREATE TRIGGER trg_cost_items_updated_at
    BEFORE UPDATE ON public.cost_items
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- ---------------------------------------------------------------------------
-- Jobs de scraping (UC14)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.scraping_jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    search_query    VARCHAR(300) NOT NULL,
    sources         TEXT[] NOT NULL DEFAULT '{}',
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    results_count   INTEGER NOT NULL DEFAULT 0,
    error_message   TEXT,
    created_by      UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_scraping_jobs_project ON public.scraping_jobs (project_id);

-- ---------------------------------------------------------------------------
-- Resultados de scraping (UC14/UC15)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.scraping_results (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id          UUID NOT NULL REFERENCES public.scraping_jobs(id) ON DELETE CASCADE,
    project_id      UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    source          VARCHAR(30) NOT NULL,
    supplier_name   VARCHAR(200) NOT NULL,
    product_name    VARCHAR(300) NOT NULL,
    price           NUMERIC(18, 2) NOT NULL,
    currency        VARCHAR(5) NOT NULL,
    product_url     TEXT,
    is_selected     BOOLEAN NOT NULL DEFAULT FALSE,
    selected_for_item_id UUID REFERENCES public.cost_items(id) ON DELETE SET NULL,
    data_hash       VARCHAR(64) NOT NULL,
    scraped_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_scraping_results_job ON public.scraping_results (job_id);
CREATE INDEX IF NOT EXISTS idx_scraping_results_project ON public.scraping_results (project_id);

-- ---------------------------------------------------------------------------
-- Orçamentos rastreáveis (UC16)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.budgets (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    budget_number       VARCHAR(50) NOT NULL UNIQUE,
    title               VARCHAR(200) NOT NULL,
    total_amount        NUMERIC(18, 2) NOT NULL,
    currency            VARCHAR(5) NOT NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'draft'
                        CHECK (status IN ('draft', 'approved', 'superseded')),
    verification_hash   VARCHAR(64) NOT NULL,
    qr_code_data        TEXT NOT NULL,
    qr_code_image       TEXT NOT NULL,
    created_by          UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    approved_by         UUID REFERENCES public.users(id) ON DELETE SET NULL,
    approved_at         TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_budgets_project ON public.budgets (project_id);
CREATE INDEX IF NOT EXISTS idx_budgets_hash ON public.budgets (verification_hash);

DROP TRIGGER IF EXISTS trg_budgets_updated_at ON public.budgets;
CREATE TRIGGER trg_budgets_updated_at
    BEFORE UPDATE ON public.budgets
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- ---------------------------------------------------------------------------
-- Linhas do orçamento (snapshot imutável com hash)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.budget_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    budget_id       UUID NOT NULL REFERENCES public.budgets(id) ON DELETE CASCADE,
    cost_item_id    UUID NOT NULL REFERENCES public.cost_items(id) ON DELETE RESTRICT,
    item_type       VARCHAR(10) NOT NULL,
    category        VARCHAR(100) NOT NULL,
    description     TEXT NOT NULL,
    quantity        NUMERIC(14, 4) NOT NULL,
    unit            VARCHAR(30) NOT NULL,
    unit_price      NUMERIC(18, 2) NOT NULL,
    total_amount    NUMERIC(18, 2) NOT NULL,
    item_hash       VARCHAR(64) NOT NULL,
    supplier_name   VARCHAR(200),
    line_order      INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_budget_items_budget ON public.budget_items (budget_id);

-- ---------------------------------------------------------------------------
-- Faturas proforma (UC17)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.proforma_invoices (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    budget_id           UUID NOT NULL REFERENCES public.budgets(id) ON DELETE RESTRICT,
    project_id          UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    invoice_number      VARCHAR(50) NOT NULL UNIQUE,
    client_name         VARCHAR(200) NOT NULL,
    client_tax_id       VARCHAR(50),
    total_amount        NUMERIC(18, 2) NOT NULL,
    currency            VARCHAR(5) NOT NULL,
    verification_hash   VARCHAR(64) NOT NULL,
    notes               TEXT,
    created_by          UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    issued_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_proforma_project ON public.proforma_invoices (project_id);

-- ---------------------------------------------------------------------------
-- Audit trail imutável de ingestão (UC18)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.audit_trail (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    entity_type     VARCHAR(30) NOT NULL,
    entity_id       UUID NOT NULL,
    action          VARCHAR(50) NOT NULL,
    actor_id        UUID REFERENCES public.users(id) ON DELETE SET NULL,
    data_hash       VARCHAR(64) NOT NULL,
    previous_hash   VARCHAR(64),
    ip_address      VARCHAR(45),
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_trail_project ON public.audit_trail (project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_trail_entity ON public.audit_trail (entity_type, entity_id);

CREATE OR REPLACE FUNCTION public.prevent_audit_trail_mutation()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'audit_trail é imutável';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_audit_trail_no_update ON public.audit_trail;
CREATE TRIGGER trg_audit_trail_no_update
    BEFORE UPDATE OR DELETE ON public.audit_trail
    FOR EACH ROW EXECUTE FUNCTION public.prevent_audit_trail_mutation();

-- ---------------------------------------------------------------------------
-- RLS
-- ---------------------------------------------------------------------------
ALTER TABLE public.cost_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scraping_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scraping_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.budgets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.budget_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.proforma_invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_trail ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_cost_items" ON public.cost_items FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_scraping_jobs" ON public.scraping_jobs FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_scraping_results" ON public.scraping_results FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_budgets" ON public.budgets FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_budget_items" ON public.budget_items FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_proforma" ON public.proforma_invoices FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_audit_trail" ON public.audit_trail FOR ALL USING (true) WITH CHECK (true);

-- Fontes de scraping pré-configuradas (MVP)
CREATE TABLE IF NOT EXISTS public.scraping_sources (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code        VARCHAR(30) NOT NULL UNIQUE,
    name        VARCHAR(100) NOT NULL,
    base_url    TEXT NOT NULL,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO public.scraping_sources (code, name, base_url) VALUES
    ('jumia', 'Jumia Angola', 'https://www.jumia.ao'),
    ('jiji', 'Jiji Angola', 'https://jiji.ao')
ON CONFLICT (code) DO NOTHING;

ALTER TABLE public.scraping_sources ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_scraping_sources" ON public.scraping_sources FOR ALL USING (true) WITH CHECK (true);
