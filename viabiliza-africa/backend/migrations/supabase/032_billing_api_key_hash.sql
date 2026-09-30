-- Terminal — API Key por projecto (hash SHA-256; chave plain só na criação/regeneração)
-- Executar após 031_terminal_billing_integration.sql

ALTER TABLE public.project_billing_integration
    ADD COLUMN IF NOT EXISTS api_key_hash VARCHAR(64);

CREATE INDEX IF NOT EXISTS idx_project_billing_integration_api_key_hash
    ON public.project_billing_integration (api_key_hash)
    WHERE api_key_hash IS NOT NULL;
