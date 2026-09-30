-- ViabilizA+ África — Módulo 2: Gestão de Projetos
-- Executar no SQL Editor do Supabase (após 001_module1_auth.sql)

-- ---------------------------------------------------------------------------
-- Projetos de viabilidade
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.projects (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id                UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    name                    VARCHAR(200) NOT NULL,
    description             TEXT,
    company_name            VARCHAR(200) NOT NULL,
    company_tax_id          VARCHAR(50),
    sector                  VARCHAR(30) NOT NULL
                            CHECK (sector IN (
                                'agriculture', 'manufacturing', 'services', 'energy',
                                'construction', 'tourism', 'technology', 'health',
                                'education', 'mining', 'retail', 'transport',
                                'real_estate', 'other'
                            )),
    country                 VARCHAR(5) NOT NULL,
    currency                VARCHAR(5) NOT NULL
                            CHECK (currency IN (
                                'USD', 'EUR', 'AOA', 'ZAR', 'NGN', 'KES',
                                'GHS', 'MZN', 'TZS', 'XOF', 'XAF'
                            )),
    investment_amount       NUMERIC(18, 2) NOT NULL CHECK (investment_amount > 0),
    project_horizon_years   INTEGER NOT NULL DEFAULT 5
                            CHECK (project_horizon_years BETWEEN 1 AND 50),
    discount_rate           NUMERIC(6, 3) CHECK (discount_rate IS NULL OR discount_rate BETWEEN 0 AND 100),
    status                  VARCHAR(20) NOT NULL DEFAULT 'draft'
                            CHECK (status IN (
                                'draft', 'in_progress', 'under_review', 'approved', 'archived'
                            )),
    has_approved_budget     BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at              TIMESTAMPTZ,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_projects_owner ON public.projects (owner_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON public.projects (status);
CREATE INDEX IF NOT EXISTS idx_projects_country ON public.projects (country);
CREATE INDEX IF NOT EXISTS idx_projects_sector ON public.projects (sector);
CREATE INDEX IF NOT EXISTS idx_projects_deleted ON public.projects (deleted_at);
CREATE INDEX IF NOT EXISTS idx_projects_created ON public.projects (created_at DESC);

DROP TRIGGER IF EXISTS trg_projects_updated_at ON public.projects;
CREATE TRIGGER trg_projects_updated_at
    BEFORE UPDATE ON public.projects
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- ---------------------------------------------------------------------------
-- Partilhas de projeto (UC11)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.project_shares (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id  UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    user_id     UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    shared_by   UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    permission  VARCHAR(20) NOT NULL DEFAULT 'view'
                CHECK (permission IN ('view', 'collaborate')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (project_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_project_shares_project ON public.project_shares (project_id);
CREATE INDEX IF NOT EXISTS idx_project_shares_user ON public.project_shares (user_id);

-- ---------------------------------------------------------------------------
-- Row Level Security
-- ---------------------------------------------------------------------------
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_shares ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_projects" ON public.projects
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "service_role_all_project_shares" ON public.project_shares
    FOR ALL USING (true) WITH CHECK (true);
