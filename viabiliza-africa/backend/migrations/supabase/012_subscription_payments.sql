-- Pagamentos de assinatura via AppyPay (Multicaixa Express / Referência)

CREATE TABLE IF NOT EXISTS public.subscription_payments (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                     UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    plan_code                   VARCHAR(30) NOT NULL,
    billing_cycle               VARCHAR(10) NOT NULL CHECK (billing_cycle IN ('monthly', 'yearly')),
    amount                      NUMERIC(12, 2) NOT NULL,
    currency                    VARCHAR(5) NOT NULL DEFAULT 'AOA',
    payment_method              VARCHAR(10) NOT NULL CHECK (payment_method IN ('gpo', 'ref')),
    status                      VARCHAR(30) NOT NULL DEFAULT 'pending'
                                CHECK (status IN ('pending', 'processing', 'paid', 'failed', 'cancelled', 'expired')),
    merchant_transaction_id     VARCHAR(64) NOT NULL UNIQUE,
    appypay_charge_id           VARCHAR(120),
    appypay_status              VARCHAR(60),
    phone_number                VARCHAR(20),
    reference_entity            VARCHAR(20),
    reference_number            VARCHAR(30),
    description                 TEXT,
    raw_response                JSONB NOT NULL DEFAULT '{}',
    error_message               TEXT,
    paid_at                     TIMESTAMPTZ,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_subscription_payments_user ON public.subscription_payments (user_id);
CREATE INDEX IF NOT EXISTS idx_subscription_payments_status ON public.subscription_payments (status);
CREATE INDEX IF NOT EXISTS idx_subscription_payments_merchant_tx ON public.subscription_payments (merchant_transaction_id);

ALTER TABLE public.subscription_payments ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "service_role_subscription_payments" ON public.subscription_payments;
CREATE POLICY "service_role_subscription_payments" ON public.subscription_payments FOR ALL USING (true) WITH CHECK (true);
