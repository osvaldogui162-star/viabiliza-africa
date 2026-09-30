-- Bancos angolanos no cadastro de projetos + metadados de taxa

ALTER TABLE public.projects
    ADD COLUMN IF NOT EXISTS bank_code VARCHAR(20),
    ADD COLUMN IF NOT EXISTS bank_rate_label TEXT,
    ADD COLUMN IF NOT EXISTS bank_rate_source_url TEXT;

CREATE INDEX IF NOT EXISTS idx_projects_bank_code ON public.projects (bank_code);
