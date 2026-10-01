-- Integração ERP/facturação por conta (planos pagos) + documentos fiscais de assinatura
-- Executar após 033_subscription_plan_features_align.sql

CREATE TABLE IF NOT EXISTS public.account_erp_billing_connections (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL UNIQUE REFERENCES public.users(id) ON DELETE CASCADE,
    provider_code           VARCHAR(40) NOT NULL,
    connection_status       VARCHAR(24) NOT NULL DEFAULT 'disconnected'
                            CHECK (connection_status IN (
                                'disconnected', 'configuring', 'connected', 'error'
                            )),
    config                  JSONB NOT NULL DEFAULT '{}'::jsonb,
    auto_fiscal_on_payment  BOOLEAN NOT NULL DEFAULT TRUE,
    last_test_at            TIMESTAMPTZ,
    last_error              TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_account_erp_billing_provider
    ON public.account_erp_billing_connections (provider_code, connection_status);

CREATE TABLE IF NOT EXISTS public.subscription_fiscal_documents (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    payment_id          UUID REFERENCES public.subscription_payments(id) ON DELETE SET NULL,
    provider_code       VARCHAR(40) NOT NULL,
    status              VARCHAR(24) NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'issued', 'export_ready', 'failed', 'skipped')),
    external_ref        VARCHAR(160),
    document_payload    JSONB NOT NULL DEFAULT '{}'::jsonb,
    agt_export_xml      TEXT,
    error_message       TEXT,
    issued_at           TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_subscription_fiscal_payment
    ON public.subscription_fiscal_documents (payment_id)
    WHERE payment_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_subscription_fiscal_user
    ON public.subscription_fiscal_documents (user_id, created_at DESC);

DROP TRIGGER IF EXISTS trg_account_erp_billing_updated_at ON public.account_erp_billing_connections;
CREATE TRIGGER trg_account_erp_billing_updated_at
    BEFORE UPDATE ON public.account_erp_billing_connections
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS trg_subscription_fiscal_documents_updated_at ON public.subscription_fiscal_documents;
CREATE TRIGGER trg_subscription_fiscal_documents_updated_at
    BEFORE UPDATE ON public.subscription_fiscal_documents
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

ALTER TABLE public.account_erp_billing_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscription_fiscal_documents ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_account_erp_billing" ON public.account_erp_billing_connections
    FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_subscription_fiscal" ON public.subscription_fiscal_documents
    FOR ALL USING (true) WITH CHECK (true);

UPDATE public.subscription_plans SET features = features || '{"erp_billing_integration":false,"erp_auto_fiscal_invoice":false}'::jsonb, updated_at = NOW()
WHERE code = 'free';

UPDATE public.subscription_plans SET features = features || '{"erp_billing_integration":true,"erp_auto_fiscal_invoice":false}'::jsonb, updated_at = NOW()
WHERE code = 'starter';

UPDATE public.subscription_plans SET features = features || '{"erp_billing_integration":true,"erp_auto_fiscal_invoice":true}'::jsonb, updated_at = NOW()
WHERE code IN ('business', 'enterprise', 'academia_institutional', 'government');
