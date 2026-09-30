-- ViabilizA+ África — Campos extendidos para criação de projecto (wizard multi-step)
-- Representante, empresa (localização), financiamento

ALTER TABLE public.projects
    ADD COLUMN IF NOT EXISTS rep_full_name VARCHAR(200),
    ADD COLUMN IF NOT EXISTS rep_email VARCHAR(200),
    ADD COLUMN IF NOT EXISTS rep_id_number VARCHAR(30),
    ADD COLUMN IF NOT EXISTS rep_phone VARCHAR(30),
    ADD COLUMN IF NOT EXISTS rep_role VARCHAR(100),
    ADD COLUMN IF NOT EXISTS company_province VARCHAR(50),
    ADD COLUMN IF NOT EXISTS company_municipality VARCHAR(100),
    ADD COLUMN IF NOT EXISTS company_address TEXT,
    ADD COLUMN IF NOT EXISTS company_activity VARCHAR(300),
    ADD COLUMN IF NOT EXISTS company_phone VARCHAR(30),
    ADD COLUMN IF NOT EXISTS company_email VARCHAR(200),
    ADD COLUMN IF NOT EXISTS company_website VARCHAR(300),
    ADD COLUMN IF NOT EXISTS company_latitude NUMERIC(10, 7),
    ADD COLUMN IF NOT EXISTS company_longitude NUMERIC(10, 7),
    ADD COLUMN IF NOT EXISTS geocode_verified BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS geocode_source VARCHAR(30),
    ADD COLUMN IF NOT EXISTS financing_type VARCHAR(50),
    ADD COLUMN IF NOT EXISTS loan_term_months INTEGER,
    ADD COLUMN IF NOT EXISTS bank_branch VARCHAR(150);

CREATE INDEX IF NOT EXISTS idx_projects_company_province ON public.projects (company_province);

COMMENT ON COLUMN public.projects.rep_id_number IS 'Número do Bilhete de Identidade do representante';
COMMENT ON COLUMN public.projects.company_province IS 'Código INE da província (Angola)';
COMMENT ON COLUMN public.projects.geocode_source IS 'google_maps | ine';
