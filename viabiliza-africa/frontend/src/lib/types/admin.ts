import type { PricingPromotion, SubscriptionPlan } from "@/lib/types/subscription";

export type AdminPromotionMatrixRow = {
  plan_code: string;
  plan_name: string;
  billing_period: string;
  billing_period_label_pt: string;
  fixed_aoa: number;
  reference_aoa: number;
  promotional_aoa: number;
  checkout_subtotal_aoa: number;
  checkout_total_aoa: number;
  promotion_applied: boolean;
};

export type AdminPromotionOverview = {
  promotion: PricingPromotion & {
    started_at?: string | null;
    duration_months?: number | null;
  };
  pricing_rules: {
    currency: string;
    vat_rate_pct: number;
    discount_basis: string;
    description_pt: string;
    description_en: string;
  };
  matrix: AdminPromotionMatrixRow[];
};

export type AdminBillingOverview = {
  users_total: number;
  subscriptions: {
    active: number;
    trial: number;
    expired: number;
    cancelled: number;
    expiring_7_days: number;
    expiring_30_days: number;
    total: number;
  };
  payments: {
    paid_total_amount: string;
    paid_currency: string;
    paid_count: number;
    pending_count: number;
    failed_count: number;
    paid_this_month_count: number;
    paid_this_month_amount: string;
  };
  subscribers_by_plan?: AdminPlanSubscriberStats[];
  recent_payments?: AdminPayment[];
  system: {
    scraping_sources: number;
    integrations: number;
    budget_templates: number;
    subscription_plans: number;
    audit_records: number;
  };
};

export type AdminPlanSubscriberStats = {
  plan_id: string;
  plan_code: string;
  plan_name: string;
  emoji?: string | null;
  active_subscribers: number;
  total_subscriptions: number;
  is_active: boolean;
};

export type AdminCustomer = {
  user: {
    id: string;
    email: string;
    full_name: string;
    role: string;
    is_active: boolean;
    preferred_currency?: string | null;
    created_at: string;
  };
  subscription: AdminUserSubscription | null;
  latest_payment: AdminPayment | null;
  projects_count: number;
  billing_status: "payment_pending" | "no_subscription" | "active" | "active_expiring" | "expired" | "trial" | string;
};

export type AdminUserSubscription = {
  id: string;
  user_id: string;
  plan_id: string;
  status: "active" | "cancelled" | "expired" | "trial";
  starts_at: string;
  ends_at: string | null;
  created_at: string;
  days_remaining: number | null;
  is_expiring_soon: boolean;
  user_email?: string;
  user_name?: string;
  plan?: SubscriptionPlan;
};

export type AdminPayment = {
  id: string;
  user_id: string;
  user_email?: string;
  user_name?: string;
  plan_code: string;
  billing_cycle: string;
  amount: string;
  currency: string;
  payment_method: string;
  status: string;
  merchant_transaction_id: string;
  paid_at: string | null;
  created_at: string;
  error_message?: string | null;
};

export type ScrapingSource = {
  id: string;
  code: string;
  name: string;
  base_url: string;
  description?: string | null;
  country: string;
  is_active: boolean;
  updated_at: string;
};

export type IntegrationSetting = {
  integration_key: string;
  settings: Record<string, unknown>;
  is_active: boolean;
  updated_at: string;
};

export type BudgetTemplate = {
  id: string;
  code: string;
  name: string;
  template_type: string;
  is_default: boolean;
  is_active: boolean;
  updated_at: string;
};

export type AuditTrailEntry = {
  id: string;
  project_id?: string | null;
  actor_id?: string | null;
  entity_type?: string;
  entity_id?: string | null;
  action?: string;
  data_hash?: string;
  previous_hash?: string | null;
  metadata?: Record<string, unknown>;
  created_at: string;
};

export type SettingsOverview = {
  scraping_sources: number;
  integrations: number;
  budget_templates: number;
  subscription_plans: number;
};

export type Paginated<T> = {
  items: T[];
  total: number;
  limit: number;
  offset: number;
};

export type AdminPlan = SubscriptionPlan;
