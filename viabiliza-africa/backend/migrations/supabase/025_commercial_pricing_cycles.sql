-- ViabilizA+ — Preços trimestral/semestral/anual, 5 planos comerciais, campanha admin

CREATE TABLE IF NOT EXISTS public.platform_settings (
    setting_key   VARCHAR(50) PRIMARY KEY,
    settings      JSONB NOT NULL DEFAULT '{}',
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO public.platform_settings (setting_key, settings)
VALUES ('pricing_promotion', '{"active": false}')
ON CONFLICT (setting_key) DO NOTHING;

ALTER TABLE public.platform_settings ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "service_role_platform_settings" ON public.platform_settings;
CREATE POLICY "service_role_platform_settings" ON public.platform_settings
    FOR ALL USING (true) WITH CHECK (true);

-- Ciclos de faturação alargados
ALTER TABLE public.subscription_payments
    DROP CONSTRAINT IF EXISTS subscription_payments_billing_cycle_check;

ALTER TABLE public.subscription_payments
    ADD CONSTRAINT subscription_payments_billing_cycle_check
    CHECK (billing_cycle IN ('monthly', 'yearly', 'quarterly', 'semiannual'));

UPDATE public.subscription_payments
SET billing_cycle = 'yearly'
WHERE billing_cycle = 'monthly';

-- Desactivar planos legados (mantém free interno)
UPDATE public.subscription_plans
SET is_active = FALSE, updated_at = NOW()
WHERE code IN ('academic', 'social_impact', 'professional');
