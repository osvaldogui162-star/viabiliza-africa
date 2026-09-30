-- ViabilizA+ — Governança de registo, convites e termos

ALTER TABLE public.users
    ADD COLUMN IF NOT EXISTS terms_accepted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS terms_version VARCHAR(20);

-- Convites pendentes (projecto ou admin) antes do registo
CREATE TABLE IF NOT EXISTS public.user_registration_invites (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) NOT NULL,
    role            VARCHAR(20) NOT NULL DEFAULT 'user'
                    CHECK (role IN ('user', 'financial')),
    invited_by      UUID REFERENCES public.users(id) ON DELETE SET NULL,
    project_id      UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    permission      VARCHAR(20) DEFAULT 'view',
    source          VARCHAR(30) NOT NULL DEFAULT 'project_share'
                    CHECK (source IN ('project_share', 'admin', 'system')),
    expires_at      TIMESTAMPTZ NOT NULL,
    consumed_at     TIMESTAMPTZ,
    consumed_by     UUID REFERENCES public.users(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reg_invites_email_pending
    ON public.user_registration_invites (lower(email), expires_at DESC)
    WHERE consumed_at IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_reg_invites_unique_pending
    ON public.user_registration_invites (lower(email), COALESCE(project_id::text, ''), source)
    WHERE consumed_at IS NULL;

ALTER TABLE public.user_registration_invites ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_reg_invites" ON public.user_registration_invites FOR ALL USING (true) WITH CHECK (true);
ç