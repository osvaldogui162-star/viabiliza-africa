-- ViabilizA+ África — Portal do financiador (acompanhamento pós-crédito)
-- Executar após 025_commercial_pricing_cycles.sql

ALTER TABLE public.users DROP CONSTRAINT IF EXISTS users_role_check;
ALTER TABLE public.users
    ADD CONSTRAINT users_role_check
    CHECK (role IN ('admin', 'financial', 'user', 'bank'));

ALTER TABLE public.users
    ADD COLUMN IF NOT EXISTS bank_code VARCHAR(20);

CREATE INDEX IF NOT EXISTS idx_users_bank_code ON public.users (bank_code)
    WHERE bank_code IS NOT NULL;

CREATE TABLE IF NOT EXISTS public.project_financing (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    bank_code           VARCHAR(20) NOT NULL,
    submission_id       UUID REFERENCES public.bank_report_submissions(id) ON DELETE SET NULL,
    decision            VARCHAR(20) NOT NULL DEFAULT 'approved'
                        CHECK (decision IN ('approved', 'conditional', 'rejected')),
    approved_amount     NUMERIC(18, 2) NOT NULL,
    currency            VARCHAR(5) NOT NULL DEFAULT 'AOA'
                        CHECK (currency IN ('USD', 'EUR', 'AOA')),
    interest_rate_pct   NUMERIC(8, 4),
    term_months         INTEGER,
    disbursed_amount    NUMERIC(18, 2) NOT NULL DEFAULT 0,
    monitoring_status   VARCHAR(20) NOT NULL DEFAULT 'on_track'
                        CHECK (monitoring_status IN ('on_track', 'attention', 'critical')),
    notes               TEXT,
    decided_by          UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    decision_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_project_financing_active
    ON public.project_financing (project_id, bank_code)
    WHERE is_active = TRUE AND decision IN ('approved', 'conditional');

CREATE INDEX IF NOT EXISTS idx_project_financing_bank
    ON public.project_financing (bank_code, decision_at DESC)
    WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_project_financing_project
    ON public.project_financing (project_id, created_at DESC);

DROP TRIGGER IF EXISTS trg_project_financing_updated_at ON public.project_financing;
CREATE TRIGGER trg_project_financing_updated_at
    BEFORE UPDATE ON public.project_financing
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

ALTER TABLE public.project_financing ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_project_financing" ON public.project_financing
    FOR ALL USING (true) WITH CHECK (true);
