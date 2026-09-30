-- ViabilizA+ África — Módulo 6: Relatórios
-- Executar após 006_kanban_trello_integration.sql

CREATE TABLE IF NOT EXISTS public.reports (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    report_type         VARCHAR(20) NOT NULL
                        CHECK (report_type IN ('international', 'bfa', 'bda')),
    language            VARCHAR(5) NOT NULL DEFAULT 'pt'
                        CHECK (language IN ('pt', 'en')),
    currency            VARCHAR(5) NOT NULL DEFAULT 'USD'
                        CHECK (currency IN ('USD', 'EUR', 'AOA')),
    title               VARCHAR(300) NOT NULL,
    verification_hash   VARCHAR(64) NOT NULL,
    pdf_storage_path    TEXT NOT NULL,
    file_size_bytes     INTEGER NOT NULL DEFAULT 0,
    qr_code_data        TEXT,
    qr_code_image       TEXT,
    metadata            JSONB NOT NULL DEFAULT '{}',
    generated_by        UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reports_project ON public.reports (project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reports_verification ON public.reports (verification_hash);

-- Links temporários WhatsApp (UC32) — validade 7 dias
CREATE TABLE IF NOT EXISTS public.report_share_links (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id   UUID NOT NULL REFERENCES public.reports(id) ON DELETE CASCADE,
    token       VARCHAR(64) NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    created_by  UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_report_share_token ON public.report_share_links (token);
CREATE INDEX IF NOT EXISTS idx_report_share_expires ON public.report_share_links (expires_at);

-- Submissões bancárias (UC34)
CREATE TABLE IF NOT EXISTS public.bank_report_submissions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id       UUID NOT NULL REFERENCES public.reports(id) ON DELETE CASCADE,
    project_id      UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    bank_code       VARCHAR(10) NOT NULL CHECK (bank_code IN ('bfa', 'bda')),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'submitted', 'accepted', 'rejected', 'error')),
    request_payload JSONB NOT NULL DEFAULT '{}',
    response_payload JSONB NOT NULL DEFAULT '{}',
    external_ref    VARCHAR(100),
    submitted_by    UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bank_submissions_project ON public.bank_report_submissions (project_id, created_at DESC);

ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.report_share_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bank_report_submissions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_reports" ON public.reports FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_report_shares" ON public.report_share_links FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_bank_submissions" ON public.bank_report_submissions FOR ALL USING (true) WITH CHECK (true);
