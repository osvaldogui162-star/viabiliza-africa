-- ViabilizA+ África — Integração Kanban externo (Trello)
-- Executar após 005_module5_collaboration.sql

ALTER TABLE public.kanban_tasks
    ADD COLUMN IF NOT EXISTS external_id VARCHAR(100),
    ADD COLUMN IF NOT EXISTS provider VARCHAR(20) NOT NULL DEFAULT 'local'
        CHECK (provider IN ('local', 'trello'));

CREATE INDEX IF NOT EXISTS idx_kanban_tasks_external
    ON public.kanban_tasks (project_id, external_id)
    WHERE external_id IS NOT NULL;

-- Ligação projeto ↔ board externo
CREATE TABLE IF NOT EXISTS public.project_kanban_integrations (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL UNIQUE REFERENCES public.projects(id) ON DELETE CASCADE,
    provider            VARCHAR(20) NOT NULL DEFAULT 'trello'
                        CHECK (provider IN ('local', 'trello')),
    external_board_id   VARCHAR(100),
    board_url           VARCHAR(500),
    list_map            JSONB NOT NULL DEFAULT '{}',
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

DROP TRIGGER IF EXISTS trg_project_kanban_integrations_updated_at ON public.project_kanban_integrations;
CREATE TRIGGER trg_project_kanban_integrations_updated_at
    BEFORE UPDATE ON public.project_kanban_integrations
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

ALTER TABLE public.project_kanban_integrations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_kanban_integrations" ON public.project_kanban_integrations
    FOR ALL USING (true) WITH CHECK (true);
