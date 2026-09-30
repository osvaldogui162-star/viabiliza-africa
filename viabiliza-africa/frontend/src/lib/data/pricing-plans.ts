import type { SubscriptionPlan } from "@/lib/types/subscription";

function plan(
  code: string,
  name: string,
  description: string,
  order: number,
  tier: "main" | "special",
  prices: { q: number; s: number; y: number; rq: number; rs: number; ry: number },
  extra: Record<string, unknown>,
): SubscriptionPlan {
  return {
    id: `fallback-${code}`,
    code,
    name,
    description,
    price_monthly: String(prices.q / 1000),
    price_yearly: String(prices.y / 1000),
    currency: "AOA",
    max_projects: (extra.max_projects as number | null | undefined) ?? null,
    max_users: (extra.max_users as number | null | undefined) ?? null,
    max_monte_carlo_iterations: (extra.max_monte_carlo_iterations as number) ?? 10000,
    features: {
      plan_tier: tier,
      billing_periods: ["quarterly", "semiannual", "yearly"],
      price_quarterly_aoa: prices.q,
      price_semiannual_aoa: prices.s,
      price_yearly_aoa: prices.y,
      reference_quarterly_aoa: prices.rq,
      reference_semiannual_aoa: prices.rs,
      reference_yearly_aoa: prices.ry,
      ...extra,
    },
    is_active: true,
    display_order: order,
    plan_tier: tier,
    price_quarterly_aoa: prices.q,
    price_semiannual_aoa: prices.s,
    price_yearly_aoa: prices.y,
    reference_quarterly_aoa: prices.rq,
    reference_semiannual_aoa: prices.rs,
    reference_yearly_aoa: prices.ry,
    billing_periods: ["quarterly", "semiannual", "yearly"],
    contact_only: Boolean(extra.contact_only),
    popular: Boolean(extra.popular),
    emoji: extra.emoji as string | undefined,
  };
}

/** Fallback alinhado ao catálogo comercial 2026 — 5 planos públicos. */
export const FALLBACK_PLANS: SubscriptionPlan[] = [
  plan(
    "starter",
    "Starter",
    "Para PMEs e consultores individuais",
    1,
    "main",
    { q: 150_000, s: 300_000, y: 550_000, rq: 187_500, rs: 375_000, ry: 687_500 },
    {
      emoji: "🚀",
      scraping: true,
      max_scraping_items_monthly: 50,
      max_projects: 20,
      max_users: 1,
      popular: true,
      support_sla: "Email (48h)",
      reports_international: true,
      reports_bfa: true,
      reports_bda: true,
      reports_aipex: true,
      bank_api: false,
      monte_carlo: true,
      sensitivity: true,
      esg_basic: true,
      digital_twin: true,
      sroi: false,
    },
  ),
  plan(
    "business",
    "Business",
    "Para empresas e consultorias de médio porte",
    2,
    "main",
    { q: 280_000, s: 550_000, y: 950_000, rq: 350_000, rs: 600_000, ry: 1_200_000 },
    {
      emoji: "🏢",
      scraping: true,
      max_scraping_items_monthly: 500,
      max_projects: null,
      max_users: 5,
      max_monte_carlo_iterations: 50000,
      support_sla: "Prioritário (24h)",
      reports_international: true,
      reports_bfa: true,
      reports_bda: true,
      reports_aipex: true,
      bank_api: true,
      monte_carlo: true,
      sensitivity: true,
      esg_basic: true,
      esg_advanced: true,
      digital_twin: true,
      sroi: true,
      priority_support: true,
    },
  ),
  plan(
    "enterprise",
    "Enterprise",
    "Para grandes empresas, bancos e organizações",
    3,
    "main",
    { q: 350_000, s: 650_000, y: 1_250_000, rq: 400_000, rs: 700_000, ry: 1_400_000 },
    {
      emoji: "👑",
      scraping: true,
      max_projects: null,
      max_users: null,
      max_monte_carlo_iterations: 50000,
      support_sla: "Dedicado (4h)",
      contact_only: true,
      reports_international: true,
      reports_bfa: true,
      reports_bda: true,
      reports_aipex: true,
      bank_api: true,
      monte_carlo: true,
      sensitivity: true,
      esg_basic: true,
      esg_advanced: true,
      digital_twin: true,
      sroi: true,
      priority_support: true,
    },
  ),
  plan(
    "academia_institutional",
    "Academia Institucional",
    "Para universidades, faculdades e centros de investigação",
    4,
    "special",
    { q: 350_000, s: 650_000, y: 1_250_000, rq: 437_500, rs: 812_500, ry: 1_562_500 },
    {
      emoji: "🏛️",
      scraping: true,
      max_projects: null,
      max_users: 50,
      max_monte_carlo_iterations: 50000,
      support_sla: "Prioritário",
      contact_only: true,
      reports_international: true,
      reports_bfa: true,
      reports_bda: true,
      reports_aipex: true,
      bank_api: true,
      monte_carlo: true,
      sensitivity: true,
      esg_basic: true,
      esg_advanced: true,
      digital_twin: true,
      sroi: true,
    },
  ),
  plan(
    "government",
    "Governo",
    "Para instituições públicas e governamentais",
    5,
    "special",
    { q: 1_000_000, s: 2_000_000, y: 3_000_000, rq: 1_250_000, rs: 2_500_000, ry: 3_750_000 },
    {
      emoji: "🏛️",
      scraping: true,
      max_projects: null,
      max_users: null,
      max_monte_carlo_iterations: 50000,
      contact_only: true,
      support_sla: "24/7",
      reports_international: true,
      reports_bfa: true,
      reports_bda: true,
      reports_aipex: true,
      bank_api: true,
      monte_carlo: true,
      sensitivity: true,
      esg_basic: true,
      esg_advanced: true,
      digital_twin: true,
      sroi: true,
      priority_support: true,
    },
  ),
];

const PLAN_FEATURE_FLAG_KEYS = [
  "reports_international",
  "reports_bfa",
  "reports_bda",
  "reports_aipex",
  "bank_api",
  "scraping",
  "monte_carlo",
  "sensitivity",
  "esg_basic",
  "esg_advanced",
  "digital_twin",
  "sroi",
  "priority_support",
  "contact_only",
] as const;

export const PLAN_FEATURE_LINES: Record<string, string[]> = {
  starter: [
    "Todos os módulos setoriais",
    "Até 20 projetos activos",
    "Scraping automático (50 itens/mês)",
    "Relatórios BFA, BDA, AIPEX, Internacional",
    "Análise de sensibilidade e cenários",
    "Suporte por email (48h)",
  ],
  business: [
    "Projetos ilimitados",
    "Scraping automático (500 itens/mês)",
    "Todos os relatórios institucionais",
    "Análise ESG integrada",
    "API e integrações (ERP, CRM)",
    "Até 5 utilizadores",
    "Suporte prioritário (24h)",
  ],
  enterprise: [
    "Projetos e scraping ilimitados",
    "Relatórios personalizáveis",
    "Análise ESG avançada",
    "Utilizadores ilimitados",
    "Formação e onboarding",
    "Consultoria incluída",
    "Suporte dedicado (4h)",
  ],
  academia_institutional: [
    "Acesso completo para professores e alunos",
    "Projetos académicos ilimitados",
    "Manual didático (Viabiliza+Academia)",
    "Formação para docentes",
    "Certificação de competências",
  ],
  government: [
    "Todos os módulos setoriais",
    "Relatórios personalizados",
    "Integração com sistemas governamentais",
    "Suporte 24/7",
    "Conformidade com lei angolana",
  ],
};

const CATALOG_PRICE_KEYS = [
  "price_quarterly_aoa",
  "price_semiannual_aoa",
  "price_yearly_aoa",
  "reference_quarterly_aoa",
  "reference_semiannual_aoa",
  "reference_yearly_aoa",
] as const;

/** Preenche preços em falta quando a API devolve planos desactualizados da BD. */
export function mergePlanWithFallback(plan: SubscriptionPlan): SubscriptionPlan {
  const fb = FALLBACK_PLANS.find((p) => p.code === plan.code);
  if (!fb) return plan;

  const merged: SubscriptionPlan = {
    ...fb,
    ...plan,
    features: { ...fb.features, ...plan.features },
  };

  for (const key of CATALOG_PRICE_KEYS) {
    if (merged[key] == null && fb[key] != null) merged[key] = fb[key];
    const featKey = key as keyof SubscriptionPlan["features"];
    if (merged.features[featKey] == null && fb.features?.[featKey] != null) {
      merged.features = { ...merged.features, [featKey]: fb.features[featKey] };
    }
  }

  for (const key of PLAN_FEATURE_FLAG_KEYS) {
    if (merged.features[key] == null && fb.features?.[key] != null) {
      merged.features = { ...merged.features, [key]: fb.features[key] };
    }
  }
  if (merged.contact_only == null && fb.contact_only != null) {
    merged.contact_only = fb.contact_only;
  }

  return merged;
}

export const COMPARISON_ROWS = [
  { label: "Projetos activos", starter: "20", business: "Ilimitado", enterprise: "Ilimitado", academia: "Ilimitado", governo: "Ilimitado" },
  { label: "Scraping automático", starter: "50/mês", business: "500/mês", enterprise: "Ilimitado", academia: "Ilimitado", governo: "Ilimitado" },
  { label: "Relatório BFA", starter: "✓", business: "✓", enterprise: "✓", academia: "✓", governo: "✓" },
  { label: "Relatório BDA", starter: "✓", business: "✓", enterprise: "✓", academia: "✓", governo: "✓" },
  { label: "Análise ESG", starter: "Básica", business: "Avançada", enterprise: "Avançada", academia: "Avançada", governo: "Avançada" },
  { label: "API e integrações", starter: "—", business: "✓", enterprise: "✓", academia: "✓", governo: "✓" },
  { label: "Utilizadores", starter: "1", business: "5", enterprise: "Ilimitado", academia: "50", governo: "Ilimitado" },
  { label: "Suporte", starter: "Email (48h)", business: "24h", enterprise: "4h", academia: "Prioritário", governo: "24/7" },
];
