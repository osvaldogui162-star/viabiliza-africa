-- Capabilities e vínculo ao escritório em convites de registo (partilha pendente)

ALTER TABLE public.user_registration_invites
    ADD COLUMN IF NOT EXISTS capabilities JSONB NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN IF NOT EXISTS office_member_id UUID REFERENCES public.analyst_office_members(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS job_title VARCHAR(120);
