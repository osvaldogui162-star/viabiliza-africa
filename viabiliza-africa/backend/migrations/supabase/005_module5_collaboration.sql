-- ViabilizA+ África — Módulo 5: Tarefas e Colaboração
-- Executar após 004_module4_analysis.sql

-- ---------------------------------------------------------------------------
-- Tarefas Kanban (UC24, UC25)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.kanban_tasks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    title           VARCHAR(200) NOT NULL,
    description     TEXT,
    assignee_id     UUID REFERENCES public.users(id) ON DELETE SET NULL,
    due_date        DATE,
    status          VARCHAR(20) NOT NULL DEFAULT 'todo'
                    CHECK (status IN ('todo', 'in_progress', 'done')),
    position        INTEGER NOT NULL DEFAULT 0,
    created_by      UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_kanban_tasks_project ON public.kanban_tasks (project_id, status, position);
CREATE INDEX IF NOT EXISTS idx_kanban_tasks_assignee ON public.kanban_tasks (assignee_id);

DROP TRIGGER IF EXISTS trg_kanban_tasks_updated_at ON public.kanban_tasks;
CREATE TRIGGER trg_kanban_tasks_updated_at
    BEFORE UPDATE ON public.kanban_tasks
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- ---------------------------------------------------------------------------
-- Dependências entre tarefas (UC26)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.task_dependencies (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    predecessor_task_id UUID NOT NULL REFERENCES public.kanban_tasks(id) ON DELETE CASCADE,
    successor_task_id   UUID NOT NULL REFERENCES public.kanban_tasks(id) ON DELETE CASCADE,
    created_by          UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (predecessor_task_id, successor_task_id),
    CHECK (predecessor_task_id <> successor_task_id)
);

CREATE INDEX IF NOT EXISTS idx_task_dependencies_project ON public.task_dependencies (project_id);
CREATE INDEX IF NOT EXISTS idx_task_dependencies_predecessor ON public.task_dependencies (predecessor_task_id);
CREATE INDEX IF NOT EXISTS idx_task_dependencies_successor ON public.task_dependencies (successor_task_id);

-- ---------------------------------------------------------------------------
-- Chat do projeto (UC27)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.project_chat_messages (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id  UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    sender_id   UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    content     TEXT NOT NULL CHECK (char_length(trim(content)) BETWEEN 1 AND 5000),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_project ON public.project_chat_messages (project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_sender ON public.project_chat_messages (sender_id);

-- ---------------------------------------------------------------------------
-- Row Level Security
-- ---------------------------------------------------------------------------
ALTER TABLE public.kanban_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.task_dependencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_chat_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_kanban_tasks" ON public.kanban_tasks FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_task_dependencies" ON public.task_dependencies FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_chat_messages" ON public.project_chat_messages FOR ALL USING (true) WITH CHECK (true);
