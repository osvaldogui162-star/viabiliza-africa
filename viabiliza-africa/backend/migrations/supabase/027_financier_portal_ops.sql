-- ViabilizA+ — Portal do banco: desembolsos, documentos, actividade
-- Executar após 026_project_financing_portal.sql

CREATE TABLE IF NOT EXISTS public.financing_disbursement (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    financing_id        UUID NOT NULL REFERENCES public.project_financing(id) ON DELETE CASCADE,
    requested_amount    NUMERIC(18, 2) NOT NULL,
    approved_amount     NUMERIC(18, 2),
    paid_amount         NUMERIC(18, 2) NOT NULL DEFAULT 0,
    currency            VARCHAR(5) NOT NULL DEFAULT 'AOA',
    status              VARCHAR(24) NOT NULL DEFAULT 'requested'
                        CHECK (status IN ('requested', 'under_review', 'approved', 'paid', 'rejected')),
    purpose             TEXT,
    requested_by        UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    reviewed_by         UUID REFERENCES public.users(id) ON DELETE SET NULL,
    requested_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    decided_at          TIMESTAMPTZ,
    paid_at             TIMESTAMPTZ,
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_financing_disbursement_financing
    ON public.financing_disbursement (financing_id, requested_at DESC);

CREATE INDEX IF NOT EXISTS idx_financing_disbursement_status
    ON public.financing_disbursement (status, requested_at DESC);

CREATE TABLE IF NOT EXISTS public.financing_document (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    financing_id        UUID NOT NULL REFERENCES public.project_financing(id) ON DELETE CASCADE,
    doc_type            VARCHAR(32) NOT NULL DEFAULT 'other'
                        CHECK (doc_type IN ('contract', 'guarantee', 'measurement', 'report', 'other')),
    title               TEXT NOT NULL,
    file_ref            TEXT,
    validation_status   VARCHAR(16) NOT NULL DEFAULT 'pending'
                        CHECK (validation_status IN ('pending', 'valid', 'rejected')),
    uploaded_by         UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    validated_by        UUID REFERENCES public.users(id) ON DELETE SET NULL,
    validated_at        TIMESTAMPTZ,
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_financing_document_financing
    ON public.financing_document (financing_id, created_at DESC);

CREATE TABLE IF NOT EXISTS public.financing_portal_activity (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bank_code           VARCHAR(20) NOT NULL,
    financing_id        UUID REFERENCES public.project_financing(id) ON DELETE SET NULL,
    project_id          UUID REFERENCES public.projects(id) ON DELETE SET NULL,
    actor_id            UUID REFERENCES public.users(id) ON DELETE SET NULL,
    actor_name          TEXT,
    action              VARCHAR(64) NOT NULL,
    summary             TEXT NOT NULL,
    metadata            JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_financing_activity_bank
    ON public.financing_portal_activity (bank_code, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_financing_activity_financing
    ON public.financing_portal_activity (financing_id, created_at DESC);

DROP TRIGGER IF EXISTS trg_financing_disbursement_updated_at ON public.financing_disbursement;
CREATE TRIGGER trg_financing_disbursement_updated_at
    BEFORE UPDATE ON public.financing_disbursement
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS trg_financing_document_updated_at ON public.financing_document;
CREATE TRIGGER trg_financing_document_updated_at
    BEFORE UPDATE ON public.financing_document
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

ALTER TABLE public.financing_disbursement ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.financing_document ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.financing_portal_activity ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_financing_disbursement" ON public.financing_disbursement
    FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_financing_document" ON public.financing_document
    FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_financing_activity" ON public.financing_portal_activity
    FOR ALL USING (true) WITH CHECK (true);
