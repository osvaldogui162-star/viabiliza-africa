-- ViabilizA+ África — Planos comerciais alinhados ao Plano de Preços v1.0 (Julho 2026)
-- Upsert dos pacotes principais e especiais; desactiva planos legados.

UPDATE public.subscription_plans
SET is_active = FALSE, updated_at = NOW()
WHERE code IN ('professional');

INSERT INTO public.subscription_plans (
    code, name, description, price_monthly, price_yearly, currency,
    max_projects, max_users, max_monte_carlo_iterations, features, is_active, display_order
) VALUES
    (
        'free', 'Gratuito', 'Plano inicial para experimentar a plataforma',
        0, 0, 'USD', 3, 1, 1000,
        '{"plan_tier":"main","scraping":false,"max_scraping_items_monthly":0,"reports_international":true,"reports_bfa":false,"reports_bda":false,"reports_aipex":false,"bank_api":false,"monte_carlo":true,"sensitivity":true,"esg_basic":false,"digital_twin":false,"sroi":false,"priority_support":false,"contact_only":false,"popular":false,"annual_discount_pct":0,"price_monthly_aoa":0,"price_yearly_aoa":0,"support_sla":"Email (72h)"}',
        TRUE, 0
    ),
    (
        'academic', 'Academic', 'Para estudantes, professores e instituições de ensino',
        15, 150, 'USD', 5, 1, 10000,
        '{"plan_tier":"main","emoji":"🎓","scraping":false,"max_scraping_items_monthly":0,"reports_international":true,"reports_bfa":true,"reports_bda":true,"reports_aipex":true,"bank_api":false,"monte_carlo":true,"sensitivity":true,"esg_basic":true,"digital_twin":false,"sroi":false,"priority_support":false,"contact_only":false,"popular":false,"annual_discount_pct":17,"price_monthly_aoa":15000,"price_yearly_aoa":150000,"support_sla":"Email (72h)"}',
        TRUE, 1
    ),
    (
        'starter', 'Starter', 'Para PMEs e consultores individuais',
        49, 490, 'USD', 20, 1, 10000,
        '{"plan_tier":"main","emoji":"🚀","scraping":true,"max_scraping_items_monthly":50,"reports_international":true,"reports_bfa":true,"reports_bda":true,"reports_aipex":true,"bank_api":false,"monte_carlo":true,"sensitivity":true,"esg_basic":true,"digital_twin":true,"sroi":false,"priority_support":false,"contact_only":false,"popular":true,"annual_discount_pct":17,"price_monthly_aoa":49000,"price_yearly_aoa":490000,"support_sla":"Email (48h)"}',
        TRUE, 2
    ),
    (
        'business', 'Business', 'Para empresas e consultorias de médio porte',
        129, 1290, 'USD', NULL, 5, 50000,
        '{"plan_tier":"main","emoji":"🏢","scraping":true,"max_scraping_items_monthly":500,"reports_international":true,"reports_bfa":true,"reports_bda":true,"reports_aipex":true,"bank_api":true,"monte_carlo":true,"sensitivity":true,"esg_basic":true,"esg_advanced":true,"digital_twin":true,"sroi":true,"priority_support":true,"contact_only":false,"popular":false,"annual_discount_pct":17,"price_monthly_aoa":129000,"price_yearly_aoa":1290000,"support_sla":"Prioritário (24h)"}',
        TRUE, 3
    ),
    (
        'enterprise', 'Enterprise', 'Para grandes empresas, bancos e organizações',
        299, 2990, 'USD', NULL, NULL, 50000,
        '{"plan_tier":"main","emoji":"👑","scraping":true,"max_scraping_items_monthly":null,"reports_international":true,"reports_bfa":true,"reports_bda":true,"reports_aipex":true,"bank_api":true,"monte_carlo":true,"sensitivity":true,"esg_basic":true,"esg_advanced":true,"digital_twin":true,"sroi":true,"priority_support":true,"onboarding":true,"consulting":true,"contact_only":true,"popular":false,"annual_discount_pct":17,"price_monthly_aoa":299000,"price_yearly_aoa":2990000,"support_sla":"Dedicado (4h)"}',
        TRUE, 4
    ),
    (
        'academia_institutional', 'Academia Institucional', 'Para universidades, faculdades e centros de investigação',
        0, 299, 'USD', NULL, 50, 50000,
        '{"plan_tier":"special","emoji":"🏛️","scraping":true,"max_scraping_items_monthly":null,"reports_international":true,"reports_bfa":true,"reports_bda":true,"reports_aipex":true,"bank_api":true,"monte_carlo":true,"sensitivity":true,"esg_basic":true,"esg_advanced":true,"digital_twin":true,"sroi":true,"priority_support":true,"yearly_only":true,"contact_only":true,"popular":false,"annual_discount_pct":0,"price_monthly_aoa":0,"price_yearly_aoa":299000,"support_sla":"Prioritário"}',
        TRUE, 5
    ),
    (
        'social_impact', 'Social Impact', 'Para ONGs e projetos sociais (50% desconto)',
        99, 990, 'USD', NULL, 5, 25000,
        '{"plan_tier":"special","emoji":"🤝","scraping":true,"max_scraping_items_monthly":200,"reports_international":true,"reports_bfa":true,"reports_bda":true,"reports_aipex":true,"bank_api":false,"monte_carlo":true,"sensitivity":true,"esg_basic":true,"esg_advanced":true,"digital_twin":true,"sroi":true,"priority_support":true,"contact_only":true,"popular":false,"annual_discount_pct":17,"price_monthly_aoa":99000,"price_yearly_aoa":990000,"support_sla":"Dedicado","vat_exempt":true}',
        TRUE, 6
    ),
    (
        'government', 'Governo', 'Para instituições públicas e governamentais',
        0, 0, 'USD', NULL, NULL, 50000,
        '{"plan_tier":"special","emoji":"🏛️","scraping":true,"max_scraping_items_monthly":null,"reports_international":true,"reports_bfa":true,"reports_bda":true,"reports_aipex":true,"bank_api":true,"monte_carlo":true,"sensitivity":true,"esg_basic":true,"esg_advanced":true,"digital_twin":true,"sroi":true,"priority_support":true,"onboarding":true,"contact_only":true,"custom_pricing":true,"popular":false,"annual_discount_pct":0,"price_monthly_aoa":0,"price_yearly_aoa":0,"support_sla":"24/7"}',
        TRUE, 7
    )
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    price_monthly = EXCLUDED.price_monthly,
    price_yearly = EXCLUDED.price_yearly,
    currency = EXCLUDED.currency,
    max_projects = EXCLUDED.max_projects,
    max_users = EXCLUDED.max_users,
    max_monte_carlo_iterations = EXCLUDED.max_monte_carlo_iterations,
    features = EXCLUDED.features,
    is_active = EXCLUDED.is_active,
    display_order = EXCLUDED.display_order,
    updated_at = NOW();

-- Actualizar preços do plano starter/enterprise legados se ainda existirem com códigos antigos
UPDATE public.subscription_plans
SET
    price_monthly = 49,
    price_yearly = 490,
    max_projects = 20,
    max_users = 1,
    updated_at = NOW()
WHERE code = 'starter';

UPDATE public.subscription_plans
SET
    price_monthly = 299,
    price_yearly = 2990,
    max_projects = NULL,
    max_users = NULL,
    updated_at = NOW()
WHERE code = 'enterprise';
