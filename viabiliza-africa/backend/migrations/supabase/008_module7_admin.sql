-- ViabilizA+ África — Módulo 7: Administração e Configuração
-- Executar após 007_module6_reports.sql

-- UC35 — Fontes de scraping configuráveis
ALTER TABLE public.scraping_sources
    ADD COLUMN IF NOT EXISTS description TEXT,
    ADD COLUMN IF NOT EXISTS country VARCHAR(5) DEFAULT 'AO',
    ADD COLUMN IF NOT EXISTS config JSONB NOT NULL DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS updated_by UUID REFERENCES public.users(id) ON DELETE SET NULL;

-- UC36 — Integrações do sistema (bancos, SMTP, Trello)
CREATE TABLE IF NOT EXISTS public.integration_settings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    integration_key VARCHAR(30) NOT NULL UNIQUE
                    CHECK (integration_key IN ('bfa', 'bda', 'smtp', 'trello')),
    settings        JSONB NOT NULL DEFAULT '{}',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    updated_by      UUID REFERENCES public.users(id) ON DELETE SET NULL,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO public.integration_settings (integration_key, settings) VALUES
    ('bfa', '{"api_url": "", "api_key": ""}'),
    ('bda', '{"api_url": "", "api_key": ""}'),
    ('smtp', '{"host": "", "port": 587, "user": "", "password": "", "from": "ViabilizA+ África <noreply@viabiliza.africa>", "use_tls": true}'),
    ('trello', '{"api_key": "", "api_token": ""}')
ON CONFLICT (integration_key) DO NOTHING;

-- UC37 — Templates de orçamento e fatura
CREATE TABLE IF NOT EXISTS public.budget_templates (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code            VARCHAR(30) NOT NULL UNIQUE,
    name            VARCHAR(100) NOT NULL,
    template_type   VARCHAR(20) NOT NULL DEFAULT 'both'
                    CHECK (template_type IN ('budget', 'proforma', 'both')),
    header_html     TEXT,
    footer_html     TEXT,
    logo_url        TEXT,
    primary_color   VARCHAR(7) DEFAULT '#1a5276',
    fields          JSONB NOT NULL DEFAULT '{}',
    is_default      BOOLEAN NOT NULL DEFAULT FALSE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_by      UUID REFERENCES public.users(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO public.budget_templates (code, name, template_type, header_html, footer_html, is_default, fields) VALUES
    (
        'institutional',
        'Institucional ViabilizA+',
        'both',
        '<h2>ViabilizA+ África</h2><p>Orçamento Rastreável</p>',
        '<p>Documento gerado automaticamente com hash SHA-256 e QR Code de verificação.</p>',
        TRUE,
        '{"show_qr": true, "show_hash": true, "show_supplier": true, "currency_label": "Moeda"}'
    )
ON CONFLICT (code) DO NOTHING;

-- UC39 — Planos e assinaturas
CREATE TABLE IF NOT EXISTS public.subscription_plans (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code                        VARCHAR(30) NOT NULL UNIQUE,
    name                        VARCHAR(100) NOT NULL,
    description                 TEXT,
    price_monthly               NUMERIC(12, 2) NOT NULL DEFAULT 0,
    price_yearly                NUMERIC(12, 2),
    currency                    VARCHAR(5) NOT NULL DEFAULT 'USD',
    max_projects                INTEGER,
    max_users                   INTEGER,
    max_monte_carlo_iterations  INTEGER NOT NULL DEFAULT 1000,
    features                    JSONB NOT NULL DEFAULT '{}',
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    display_order               INTEGER NOT NULL DEFAULT 0,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO public.subscription_plans (
    code, name, description, price_monthly, price_yearly, max_projects,
    max_monte_carlo_iterations, features, display_order
) VALUES
    (
        'free', 'Gratuito', 'Plano inicial para experimentar a plataforma',
        0, 0, 3, 1000,
        '{"scraping": true, "reports_international": true, "reports_bfa": false, "reports_bda": false, "bank_api": false, "monte_carlo": true, "sensitivity": true}',
        1
    ),
    (
        'starter', 'Starter', 'Para analistas independentes',
        29.99, 299.99, 10, 10000,
        '{"scraping": true, "reports_international": true, "reports_bfa": true, "reports_bda": false, "bank_api": false, "monte_carlo": true, "sensitivity": true}',
        2
    ),
    (
        'professional', 'Profissional', 'Para equipas de consultoria',
        79.99, 799.99, 50, 50000,
        '{"scraping": true, "reports_international": true, "reports_bfa": true, "reports_bda": true, "bank_api": true, "monte_carlo": true, "sensitivity": true}',
        3
    ),
    (
        'enterprise', 'Empresarial', 'Sem limites — grandes organizações',
        199.99, 1999.99, NULL, 50000,
        '{"scraping": true, "reports_international": true, "reports_bfa": true, "reports_bda": true, "bank_api": true, "monte_carlo": true, "sensitivity": true, "priority_support": true}',
        4
    )
ON CONFLICT (code) DO NOTHING;

CREATE TABLE IF NOT EXISTS public.user_subscriptions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    plan_id     UUID NOT NULL REFERENCES public.subscription_plans(id) ON DELETE RESTRICT,
    status      VARCHAR(20) NOT NULL DEFAULT 'active'
                CHECK (status IN ('active', 'cancelled', 'expired', 'trial')),
    starts_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ends_at     TIMESTAMPTZ,
    created_by  UUID REFERENCES public.users(id) ON DELETE SET NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user ON public.user_subscriptions (user_id, status);
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_subscriptions_active
    ON public.user_subscriptions (user_id) WHERE status = 'active';

ALTER TABLE public.integration_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.budget_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscription_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_subscriptions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_integration_settings" ON public.integration_settings;
DROP POLICY IF EXISTS "service_role_budget_templates" ON public.budget_templates;
DROP POLICY IF EXISTS "service_role_subscription_plans" ON public.subscription_plans;
DROP POLICY IF EXISTS "service_role_user_subscriptions" ON public.user_subscriptions;

CREATE POLICY "service_role_integration_settings" ON public.integration_settings FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_budget_templates" ON public.budget_templates FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_subscription_plans" ON public.subscription_plans FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_user_subscriptions" ON public.user_subscriptions FOR ALL USING (true) WITH CHECK (true);
