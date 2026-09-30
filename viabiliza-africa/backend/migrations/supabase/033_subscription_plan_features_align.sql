-- Alinha features dos planos com plan_feature_matrix / catálogo comercial (pós-sync)
-- Executar após 032; alternativa: Admin → Sincronizar planos com catálogo

UPDATE public.subscription_plans SET features = features || '{"reports_bfa":false,"reports_bda":false,"reports_aipex":false,"bank_api":false,"monte_carlo":true,"sensitivity":true}'::jsonb, updated_at = NOW()
WHERE code = 'free';

UPDATE public.subscription_plans SET features = features || '{"reports_international":true,"reports_bfa":true,"reports_bda":true,"reports_aipex":true,"bank_api":false,"monte_carlo":true,"sensitivity":true,"esg_basic":true,"digital_twin":true,"sroi":false,"scraping":true,"max_scraping_items_monthly":50}'::jsonb, updated_at = NOW()
WHERE code = 'starter';

UPDATE public.subscription_plans SET features = features || '{"reports_international":true,"reports_bfa":true,"reports_bda":true,"reports_aipex":true,"bank_api":true,"monte_carlo":true,"sensitivity":true,"esg_basic":true,"esg_advanced":true,"digital_twin":true,"sroi":true,"priority_support":true,"scraping":true,"max_scraping_items_monthly":500}'::jsonb, updated_at = NOW()
WHERE code = 'business';

UPDATE public.subscription_plans SET features = features || '{"reports_international":true,"reports_bfa":true,"reports_bda":true,"reports_aipex":true,"bank_api":true,"monte_carlo":true,"sensitivity":true,"esg_basic":true,"esg_advanced":true,"digital_twin":true,"sroi":true,"priority_support":true,"scraping":true,"contact_only":true}'::jsonb, updated_at = NOW()
WHERE code = 'enterprise';

UPDATE public.subscription_plans SET features = features || '{"reports_international":true,"reports_bfa":true,"reports_bda":true,"reports_aipex":true,"bank_api":true,"monte_carlo":true,"sensitivity":true,"esg_basic":true,"esg_advanced":true,"digital_twin":true,"sroi":true,"priority_support":true,"scraping":true,"contact_only":true}'::jsonb, updated_at = NOW()
WHERE code = 'academia_institutional';

UPDATE public.subscription_plans SET features = features || '{"reports_international":true,"reports_bfa":true,"reports_bda":true,"reports_aipex":true,"bank_api":true,"monte_carlo":true,"sensitivity":true,"esg_basic":true,"esg_advanced":true,"digital_twin":true,"sroi":true,"priority_support":true,"scraping":true,"contact_only":true,"onboarding":true}'::jsonb, updated_at = NOW()
WHERE code = 'government';
