-- ViabilizA+ África — Módulo 4: Análise e Indicadores
-- Executar após 003_module3_ingestion.sql

-- ---------------------------------------------------------------------------
-- Pressupostos financeiros por projeto
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.financial_assumptions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL UNIQUE REFERENCES public.projects(id) ON DELETE CASCADE,
    assumptions     JSONB NOT NULL DEFAULT '{}',
    updated_by      UUID REFERENCES public.users(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

DROP TRIGGER IF EXISTS trg_financial_assumptions_updated_at ON public.financial_assumptions;
CREATE TRIGGER trg_financial_assumptions_updated_at
    BEFORE UPDATE ON public.financial_assumptions
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- ---------------------------------------------------------------------------
-- Análises de indicadores (UC19)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.financial_analyses (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    assumptions         JSONB NOT NULL,
    cash_flows          JSONB NOT NULL,
    indicators          JSONB NOT NULL,
    indicators_count    INTEGER NOT NULL DEFAULT 0,
    calculation_hash    VARCHAR(64) NOT NULL,
    created_by          UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_financial_analyses_project ON public.financial_analyses (project_id, created_at DESC);

-- ---------------------------------------------------------------------------
-- Simulações Monte Carlo (UC20)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.monte_carlo_simulations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    iterations      INTEGER NOT NULL CHECK (iterations BETWEEN 1000 AND 50000),
    parameters      JSONB NOT NULL,
    results         JSONB NOT NULL,
    analysis_id     UUID REFERENCES public.financial_analyses(id) ON DELETE SET NULL,
    created_by      UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_monte_carlo_project ON public.monte_carlo_simulations (project_id, created_at DESC);

-- ---------------------------------------------------------------------------
-- Análises de sensibilidade (UC21)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.sensitivity_analyses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    variables       JSONB NOT NULL,
    results         JSONB NOT NULL,
    analysis_id     UUID REFERENCES public.financial_analyses(id) ON DELETE SET NULL,
    created_by      UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sensitivity_project ON public.sensitivity_analyses (project_id, created_at DESC);

-- ---------------------------------------------------------------------------
-- Benchmarks de mercado africano (UC22)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.sector_benchmarks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sector          VARCHAR(30) NOT NULL,
    country         VARCHAR(5),
    metric_key      VARCHAR(50) NOT NULL,
    metric_label    VARCHAR(100) NOT NULL,
    average_value   NUMERIC(18, 6) NOT NULL,
    unit            VARCHAR(20) NOT NULL DEFAULT '%',
    source          VARCHAR(200) NOT NULL DEFAULT 'Média setorial africana',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (sector, country, metric_key)
);

CREATE INDEX IF NOT EXISTS idx_sector_benchmarks_sector ON public.sector_benchmarks (sector);

-- Dados de referência — médias setoriais africanas (MVP)
INSERT INTO public.sector_benchmarks (sector, country, metric_key, metric_label, average_value, unit) VALUES
    ('agriculture', NULL, 'irr', 'TIR Média', 18.5, '%'),
    ('agriculture', NULL, 'roi', 'ROI Média', 22.0, '%'),
    ('agriculture', NULL, 'npv_margin', 'Margem VPL/Investimento', 35.0, '%'),
    ('agriculture', NULL, 'payback_years', 'Payback Médio', 4.5, 'anos'),
    ('agriculture', NULL, 'ebitda_margin', 'Margem EBITDA', 28.0, '%'),
    ('manufacturing', NULL, 'irr', 'TIR Média', 16.0, '%'),
    ('manufacturing', NULL, 'roi', 'ROI Média', 20.0, '%'),
    ('manufacturing', NULL, 'npv_margin', 'Margem VPL/Investimento', 30.0, '%'),
    ('manufacturing', NULL, 'payback_years', 'Payback Médio', 5.0, 'anos'),
    ('manufacturing', NULL, 'ebitda_margin', 'Margem EBITDA', 22.0, '%'),
    ('technology', NULL, 'irr', 'TIR Média', 25.0, '%'),
    ('technology', NULL, 'roi', 'ROI Média', 35.0, '%'),
    ('technology', NULL, 'npv_margin', 'Margem VPL/Investimento', 45.0, '%'),
    ('technology', NULL, 'payback_years', 'Payback Médio', 3.5, 'anos'),
    ('technology', NULL, 'ebitda_margin', 'Margem EBITDA', 32.0, '%'),
    ('energy', NULL, 'irr', 'TIR Média', 14.0, '%'),
    ('energy', NULL, 'roi', 'ROI Média', 18.0, '%'),
    ('energy', NULL, 'npv_margin', 'Margem VPL/Investimento', 28.0, '%'),
    ('energy', NULL, 'payback_years', 'Payback Médio', 6.0, 'anos'),
    ('energy', NULL, 'ebitda_margin', 'Margem EBITDA', 35.0, '%'),
    ('construction', NULL, 'irr', 'TIR Média', 15.0, '%'),
    ('construction', NULL, 'roi', 'ROI Média', 19.0, '%'),
    ('construction', NULL, 'npv_margin', 'Margem VPL/Investimento', 25.0, '%'),
    ('construction', NULL, 'payback_years', 'Payback Médio', 5.5, 'anos'),
    ('construction', NULL, 'ebitda_margin', 'Margem EBITDA', 18.0, '%'),
    ('services', NULL, 'irr', 'TIR Média', 20.0, '%'),
    ('services', NULL, 'roi', 'ROI Média', 24.0, '%'),
    ('services', NULL, 'npv_margin', 'Margem VPL/Investimento', 38.0, '%'),
    ('services', NULL, 'payback_years', 'Payback Médio', 4.0, 'anos'),
    ('services', NULL, 'ebitda_margin', 'Margem EBITDA', 25.0, '%'),
    ('tourism', NULL, 'irr', 'TIR Média', 17.0, '%'),
    ('tourism', NULL, 'roi', 'ROI Média', 21.0, '%'),
    ('tourism', NULL, 'npv_margin', 'Margem VPL/Investimento', 32.0, '%'),
    ('tourism', NULL, 'payback_years', 'Payback Médio', 4.8, 'anos'),
    ('tourism', NULL, 'ebitda_margin', 'Margem EBITDA', 30.0, '%'),
    ('health', NULL, 'irr', 'TIR Média', 16.5, '%'),
    ('health', NULL, 'roi', 'ROI Média', 19.5, '%'),
    ('health', NULL, 'npv_margin', 'Margem VPL/Investimento', 28.0, '%'),
    ('health', NULL, 'payback_years', 'Payback Médio', 5.2, 'anos'),
    ('health', NULL, 'ebitda_margin', 'Margem EBITDA', 20.0, '%'),
    ('retail', NULL, 'irr', 'TIR Média', 19.0, '%'),
    ('retail', NULL, 'roi', 'ROI Média', 23.0, '%'),
    ('retail', NULL, 'npv_margin', 'Margem VPL/Investimento', 33.0, '%'),
    ('retail', NULL, 'payback_years', 'Payback Médio', 4.2, 'anos'),
    ('retail', NULL, 'ebitda_margin', 'Margem EBITDA', 15.0, '%'),
    ('mining', NULL, 'irr', 'TIR Média', 13.0, '%'),
    ('mining', NULL, 'roi', 'ROI Média', 17.0, '%'),
    ('mining', NULL, 'npv_margin', 'Margem VPL/Investimento', 40.0, '%'),
    ('mining', NULL, 'payback_years', 'Payback Médio', 7.0, 'anos'),
    ('mining', NULL, 'ebitda_margin', 'Margem EBITDA', 40.0, '%'),
    ('other', NULL, 'irr', 'TIR Média', 17.0, '%'),
    ('other', NULL, 'roi', 'ROI Média', 20.0, '%'),
    ('other', NULL, 'npv_margin', 'Margem VPL/Investimento', 30.0, '%'),
    ('other', NULL, 'payback_years', 'Payback Médio', 5.0, 'anos'),
    ('other', NULL, 'ebitda_margin', 'Margem EBITDA', 22.0, '%')
ON CONFLICT (sector, country, metric_key) DO NOTHING;

-- RLS
ALTER TABLE public.financial_assumptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.financial_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.monte_carlo_simulations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sensitivity_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sector_benchmarks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_financial_assumptions" ON public.financial_assumptions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_financial_analyses" ON public.financial_analyses FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_monte_carlo" ON public.monte_carlo_simulations FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_sensitivity" ON public.sensitivity_analyses FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_benchmarks" ON public.sector_benchmarks FOR ALL USING (true) WITH CHECK (true);
