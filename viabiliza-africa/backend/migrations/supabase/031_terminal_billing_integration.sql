-- Terminal Viabiliza+África — integração obrigatória com sistema de facturação
-- Executar após 030_invite_share_capabilities.sql

CREATE TABLE IF NOT EXISTS public.project_billing_integration (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL UNIQUE REFERENCES public.projects(id) ON DELETE CASCADE,
    erp_label           VARCHAR(120),
    connection_status   VARCHAR(24) NOT NULL DEFAULT 'pending'
                        CHECK (connection_status IN (
                            'pending', 'integrating', 'authenticated', 'syncing', 'active', 'error', 'disconnected'
                        )),
    api_key_hint        VARCHAR(16),
    last_sync_at        TIMESTAMPTZ,
    last_hash           VARCHAR(64),
    latest_snapshot     JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_project_billing_integration_status
    ON public.project_billing_integration (connection_status, updated_at DESC);

CREATE TABLE IF NOT EXISTS public.project_billing_sync_event (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    payload_hash        VARCHAR(64) NOT NULL,
    payload             JSONB NOT NULL,
    synced_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_project_billing_sync_project
    ON public.project_billing_sync_event (project_id, synced_at DESC);

DROP TRIGGER IF EXISTS trg_project_billing_integration_updated_at ON public.project_billing_integration;
CREATE TRIGGER trg_project_billing_integration_updated_at
    BEFORE UPDATE ON public.project_billing_integration
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

ALTER TABLE public.project_billing_integration ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_billing_sync_event ENABLE ROW LEVEL SECURITY;
