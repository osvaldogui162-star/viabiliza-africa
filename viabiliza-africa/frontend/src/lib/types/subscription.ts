export type BillingPeriod = "quarterly" | "semiannual" | "yearly";
/** @deprecated use BillingPeriod — monthly mapeia para quarterly na API */
export type BillingCycle = BillingPeriod | "monthly";
export type CurrencyDisplay = "USD" | "AOA";

export interface PricingPromotion {
  active: boolean;
  discount_pct?: number;
  ends_at?: string | null;
  label_pt?: string | null;
  label_en?: string | null;
}

export interface PlanRecommendation {
  headline_pt?: string;
  headline_en?: string;
  reason_pt?: string;
  reason_en?: string;
  upgrade_pt?: string;
  upgrade_en?: string;
}

export interface PlanPricingPreview {
  currency?: string;
  subtotal?: string;
  price_fixed_aoa?: number;
  price_reference_aoa?: number;
  price_promotional_aoa?: number;
  promotion_applied?: boolean;
}
export type PaymentMethod = "bank_transfer" | "multicaixa" | "card" | "paypal" | "mpesa";

export interface SubscriptionPlanFeatures {
  plan_tier?: "main" | "special";
  emoji?: string;
  scraping?: boolean;
  max_scraping_items_monthly?: number | null;
  reports_international?: boolean;
  reports_bfa?: boolean;
  reports_bda?: boolean;
  reports_aipex?: boolean;
  bank_api?: boolean;
  monte_carlo?: boolean;
  sensitivity?: boolean;
  esg_basic?: boolean;
  esg_advanced?: boolean;
  digital_twin?: boolean;
  sroi?: boolean;
  priority_support?: boolean;
  contact_only?: boolean;
  popular?: boolean;
  yearly_only?: boolean;
  annual_discount_pct?: number;
  price_monthly_aoa?: number;
  price_yearly_aoa?: number;
  price_quarterly_aoa?: number;
  price_semiannual_aoa?: number;
  reference_quarterly_aoa?: number;
  reference_semiannual_aoa?: number;
  reference_yearly_aoa?: number;
  billing_periods?: BillingPeriod[];
  support_sla?: string;
  onboarding?: boolean;
  consulting?: boolean;
  custom_pricing?: boolean;
  vat_exempt?: boolean;
}

export interface SubscriptionPlan {
  id: string;
  code: string;
  name: string;
  description: string | null;
  price_monthly: string;
  price_yearly: string | null;
  currency: string;
  max_projects: number | null;
  max_users: number | null;
  max_monte_carlo_iterations: number;
  features: SubscriptionPlanFeatures;
  is_active: boolean;
  display_order: number;
  plan_tier?: string;
  popular?: boolean;
  contact_only?: boolean;
  yearly_only?: boolean;
  emoji?: string;
  annual_discount_pct?: number;
  price_monthly_aoa?: number;
  price_yearly_aoa?: number;
  price_quarterly_aoa?: number;
  price_semiannual_aoa?: number;
  reference_quarterly_aoa?: number;
  reference_semiannual_aoa?: number;
  reference_yearly_aoa?: number;
  billing_periods?: BillingPeriod[];
  recommendation?: PlanRecommendation;
  support_sla?: string;
  hidden_from_pricing?: boolean;
  pricing_preview?: Partial<Record<BillingPeriod, PlanPricingPreview>>;
}

export interface SubscriptionUsage {
  projects_count: number;
  projects_limit: number | null;
  scraping_items_this_month: number;
  scraping_items_limit: number | null;
  collaborators_count: number;
  team_members_limit: number | null;
  monte_carlo_iterations_limit: number;
}

export interface PlanCapabilities {
  plan_code: string;
  plan_name: string;
  support_sla?: string | null;
  projects_limit: number | null;
  projects_limit_label: string;
  team_members_limit: number | null;
  team_members_limit_label: string;
  monte_carlo_iterations_limit: number;
  scraping_enabled: boolean;
  auto_ingestion_enabled: boolean;
  scraping_monthly_limit: number | null;
  scraping_limit_label: string;
  monte_carlo_enabled: boolean;
  sensitivity_enabled: boolean;
  reports_international: boolean;
  reports_bfa: boolean;
  reports_bda: boolean;
  reports_aipex: boolean;
  bank_api_enabled: boolean;
  esg_enabled: boolean;
  esg_advanced_enabled: boolean;
  digital_twin_enabled: boolean;
  sroi_enabled: boolean;
  priority_support: boolean;
  erp_billing_integration?: boolean;
  erp_auto_fiscal_invoice?: boolean;
}

export interface MySubscriptionResponse {
  plan: SubscriptionPlan;
  subscription: {
    id: string;
    plan_id: string;
    status: string;
    starts_at: string;
    ends_at: string | null;
  } | null;
  usage: SubscriptionUsage;
  capabilities: PlanCapabilities;
  is_implicit_free: boolean;
  promotion?: PricingPromotion;
}

export interface PlansResponse {
  items: SubscriptionPlan[];
  total: number;
  promotion?: PricingPromotion;
  billing_periods?: Array<{ code: BillingPeriod; label_pt: string; label_en: string }>;
}

export interface SubscribeResponse {
  message: string;
  billing_cycle: BillingCycle;
  currency: string;
  payment_method?: PaymentMethod;
  reference?: string;
  amount?: {
    currency: string;
    subtotal: string;
    vat: string;
    total: string;
    vat_rate_pct: number;
  };
  subscription: {
    id: string;
    plan_id: string;
    status: string;
    plan?: SubscriptionPlan;
  };
}

export interface CheckoutResponse {
  plan: SubscriptionPlan;
  billing_cycle: BillingCycle;
  amount: {
    currency: string;
    subtotal: string;
    vat: string;
    total: string;
    vat_rate_pct: number;
  };
  payment_methods: { code: PaymentMethod; label: string }[];
  appypay?: {
    sandbox: boolean;
    sandbox_gpo_phones?: Array<{
      number: string;
      label: string;
      description?: string;
    }>;
    gpo_note?: string | null;
  };
}
