-- Missão, Visão, Valores, SWOT, riscos e incentivos AIPEX

ALTER TABLE public.projects
    ADD COLUMN IF NOT EXISTS mission TEXT,
    ADD COLUMN IF NOT EXISTS vision TEXT,
    ADD COLUMN IF NOT EXISTS core_values JSONB NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS swot_analysis JSONB NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN IF NOT EXISTS risk_register JSONB NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS aipex_incentives JSONB NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS strategic_generated_at TIMESTAMPTZ;

COMMENT ON COLUMN public.projects.swot_analysis IS 'Análise SWOT automática (strengths, weaknesses, opportunities, threats)';
COMMENT ON COLUMN public.projects.aipex_incentives IS 'Incentivos fiscais AIPEX aplicáveis ao sector';
