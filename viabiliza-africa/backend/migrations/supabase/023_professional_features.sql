-- ViabilizA+ — Notificações, chat read/presence, Kanban review, scraping logs

-- Kanban: estado "review"
ALTER TABLE public.kanban_tasks DROP CONSTRAINT IF EXISTS kanban_tasks_status_check;
ALTER TABLE public.kanban_tasks
    ADD CONSTRAINT kanban_tasks_status_check
    CHECK (status IN ('todo', 'in_progress', 'review', 'done'));

-- Notificações in-app
CREATE TABLE IF NOT EXISTS public.user_notifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    type            VARCHAR(40) NOT NULL,
    title           VARCHAR(200) NOT NULL,
    body            TEXT,
    href            VARCHAR(500),
    project_id      UUID REFERENCES public.projects(id) ON DELETE SET NULL,
    metadata        JSONB NOT NULL DEFAULT '{}',
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_notifications_user ON public.user_notifications (user_id, is_read, created_at DESC);

-- Leitura do chat por utilizador/projecto
CREATE TABLE IF NOT EXISTS public.project_chat_read_state (
    user_id             UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    project_id          UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    last_read_message_id UUID REFERENCES public.project_chat_messages(id) ON DELETE SET NULL,
    last_read_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, project_id)
);

-- Presença online (heartbeat)
CREATE TABLE IF NOT EXISTS public.project_presence (
    user_id         UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    project_id      UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    last_seen_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, project_id)
);

CREATE INDEX IF NOT EXISTS idx_project_presence_project ON public.project_presence (project_id, last_seen_at DESC);

-- Logs de execução de scraping (admin)
CREATE TABLE IF NOT EXISTS public.scraping_run_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id       UUID REFERENCES public.scraping_sources(id) ON DELETE SET NULL,
    source_code     VARCHAR(80),
    project_id      UUID REFERENCES public.projects(id) ON DELETE SET NULL,
    user_id         UUID REFERENCES public.users(id) ON DELETE SET NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'success' CHECK (status IN ('success', 'partial', 'failed')),
    items_found     INTEGER NOT NULL DEFAULT 0,
    message         TEXT,
    duration_ms     INTEGER,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_scraping_run_logs_created ON public.scraping_run_logs (created_at DESC);

ALTER TABLE public.user_notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_chat_read_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_presence ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scraping_run_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_user_notifications" ON public.user_notifications FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_chat_read" ON public.project_chat_read_state FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_presence" ON public.project_presence FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_scraping_logs" ON public.scraping_run_logs FOR ALL USING (true) WITH CHECK (true);
