-- ViabilizA+ — Fluxo de aprovação bancária (submissão → decisão → acompanhamento)
-- Executar após 027_financier_portal_ops.sql

ALTER TABLE public.project_financing DROP CONSTRAINT IF EXISTS project_financing_decision_check;
ALTER TABLE public.project_financing
    ADD CONSTRAINT project_financing_decision_check
    CHECK (decision IN ('pending', 'approved', 'conditional', 'rejected'));

ALTER TABLE public.project_financing
    ADD COLUMN IF NOT EXISTS workflow_status VARCHAR(24) NOT NULL DEFAULT 'active'
        CHECK (workflow_status IN ('pending_bank', 'active', 'rejected', 'closed'));

ALTER TABLE public.project_financing
    ADD COLUMN IF NOT EXISTS submitted_by UUID REFERENCES public.users(id) ON DELETE SET NULL;

ALTER TABLE public.project_financing
    ADD COLUMN IF NOT EXISTS bank_decided_by UUID REFERENCES public.users(id) ON DELETE SET NULL;

ALTER TABLE public.project_financing
    ADD COLUMN IF NOT EXISTS bank_decided_at TIMESTAMPTZ;

UPDATE public.project_financing
SET
    workflow_status = CASE
        WHEN decision = 'rejected' THEN 'rejected'
        ELSE 'active'
    END,
    submitted_by = COALESCE(submitted_by, decided_by)
WHERE submitted_by IS NULL;

DROP INDEX IF EXISTS idx_project_financing_active;
CREATE UNIQUE INDEX IF NOT EXISTS idx_project_financing_active
    ON public.project_financing (project_id, bank_code)
    WHERE is_active = TRUE
      AND workflow_status = 'active'
      AND decision IN ('approved', 'conditional');

CREATE UNIQUE INDEX IF NOT EXISTS idx_project_financing_pending_bank
    ON public.project_financing (project_id, bank_code)
    WHERE is_active = TRUE
      AND workflow_status = 'pending_bank'
      AND decision = 'pending';

CREATE INDEX IF NOT EXISTS idx_project_financing_pending_list
    ON public.project_financing (bank_code, created_at DESC)
    WHERE is_active = TRUE AND workflow_status = 'pending_bank';
