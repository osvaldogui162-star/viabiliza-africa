-- ViabilizA+ — Meu escritório (equipa do analista + capacidades por projecto)
-- Executar após 028_financing_approval_workflow.sql

CREATE TABLE IF NOT EXISTS public.analyst_office_members (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id        UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    user_id         UUID REFERENCES public.users(id) ON DELETE SET NULL,
    email           VARCHAR(255) NOT NULL,
    full_name       VARCHAR(200) NOT NULL,
    job_title       VARCHAR(120) NOT NULL DEFAULT 'Colaborador',
    status          VARCHAR(20) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'archived')),
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_office_member_owner_email
    ON public.analyst_office_members (owner_id, lower(email))
    WHERE status = 'active';

CREATE INDEX IF NOT EXISTS idx_office_members_owner
    ON public.analyst_office_members (owner_id, status, created_at DESC);

ALTER TABLE public.project_shares
    ADD COLUMN IF NOT EXISTS office_member_id UUID
        REFERENCES public.analyst_office_members(id) ON DELETE SET NULL;

ALTER TABLE public.project_shares
    ADD COLUMN IF NOT EXISTS job_title VARCHAR(120);

ALTER TABLE public.project_shares
    ADD COLUMN IF NOT EXISTS capabilities JSONB NOT NULL DEFAULT '{}'::jsonb;

CREATE INDEX IF NOT EXISTS idx_project_shares_office_member
    ON public.project_shares (office_member_id)
    WHERE office_member_id IS NOT NULL;

DROP TRIGGER IF EXISTS trg_analyst_office_members_updated_at ON public.analyst_office_members;
CREATE TRIGGER trg_analyst_office_members_updated_at
    BEFORE UPDATE ON public.analyst_office_members
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

ALTER TABLE public.analyst_office_members ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_analyst_office_members" ON public.analyst_office_members
    FOR ALL USING (true) WITH CHECK (true);
