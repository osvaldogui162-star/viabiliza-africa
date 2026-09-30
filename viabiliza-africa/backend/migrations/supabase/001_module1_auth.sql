-- ViabilizA+ África — Módulo 1: Autenticação e Gestão de Acesso
-- Executar no SQL Editor do Supabase

-- Extensão para UUID
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ---------------------------------------------------------------------------
-- Tabela de utilizadores
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(200) NOT NULL,
    role            VARCHAR(20)  NOT NULL DEFAULT 'user'
                    CHECK (role IN ('admin', 'financial', 'user')),
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON public.users (email);
CREATE INDEX IF NOT EXISTS idx_users_role ON public.users (role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON public.users (is_active);

-- Trigger para updated_at automático
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_users_updated_at ON public.users;
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- ---------------------------------------------------------------------------
-- Tokens de recuperação de palavra-passe
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.password_reset_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    token_hash  VARCHAR(64) NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_password_reset_user ON public.password_reset_tokens (user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_hash ON public.password_reset_tokens (token_hash);

-- ---------------------------------------------------------------------------
-- Refresh tokens (sessões)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.refresh_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    token_hash  VARCHAR(64) NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON public.refresh_tokens (user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_hash ON public.refresh_tokens (token_hash);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires ON public.refresh_tokens (expires_at);

-- ---------------------------------------------------------------------------
-- Logs de acesso e auditoria (imutáveis — apenas INSERT)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.access_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES public.users(id) ON DELETE SET NULL,
    action      VARCHAR(50) NOT NULL,
    ip_address  VARCHAR(45),
    user_agent  TEXT,
    metadata    JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_access_logs_user ON public.access_logs (user_id);
CREATE INDEX IF NOT EXISTS idx_access_logs_action ON public.access_logs (action);
CREATE INDEX IF NOT EXISTS idx_access_logs_created ON public.access_logs (created_at DESC);

-- Impedir UPDATE/DELETE nos logs (audit trail imutável)
CREATE OR REPLACE FUNCTION public.prevent_access_log_mutation()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'access_logs é imutável — operações UPDATE/DELETE não permitidas';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_access_logs_no_update ON public.access_logs;
CREATE TRIGGER trg_access_logs_no_update
    BEFORE UPDATE ON public.access_logs
    FOR EACH ROW EXECUTE FUNCTION public.prevent_access_log_mutation();

DROP TRIGGER IF EXISTS trg_access_logs_no_delete ON public.access_logs;
CREATE TRIGGER trg_access_logs_no_delete
    BEFORE DELETE ON public.access_logs
    FOR EACH ROW EXECUTE FUNCTION public.prevent_access_log_mutation();

-- ---------------------------------------------------------------------------
-- Row Level Security (RLS) — desactivado; backend usa service_role key
-- ---------------------------------------------------------------------------
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.password_reset_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.refresh_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.access_logs ENABLE ROW LEVEL SECURITY;

-- Políticas permissivas para service_role (backend)
CREATE POLICY "service_role_all_users" ON public.users
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "service_role_all_reset_tokens" ON public.password_reset_tokens
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "service_role_all_refresh_tokens" ON public.refresh_tokens
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "service_role_all_access_logs" ON public.access_logs
    FOR ALL USING (true) WITH CHECK (true);
