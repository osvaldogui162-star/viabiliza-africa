import { apiRequest, buildQuery } from "@/lib/api/http-client";
import type {
  AdminBillingOverview,
  AdminCustomer,
  AdminPayment,
  AdminPlan,
  AdminPromotionOverview,
  AdminUserSubscription,
  AuditTrailEntry,
  BudgetTemplate,
  IntegrationSetting,
  Paginated,
  ScrapingSource,
  SettingsOverview,
} from "@/lib/types/admin";

export type { SettingsOverview, AdminPlan as SubscriptionPlan } from "@/lib/types/admin";

export interface AccessLog {
  id: string;
  user_id: string;
  user_email: string;
  user_name: string;
  action: string;
  ip_address: string | null;
  user_agent: string | null;
  created_at: string;
}

export const adminApi = {
  billingOverview() {
    return apiRequest<AdminBillingOverview>("/admin/billing/overview", "GET");
  },

  settingsOverview() {
    return apiRequest<SettingsOverview>("/admin/settings/overview", "GET");
  },

  accessLogs(params?: {
    user_id?: string;
    action?: string;
    from_date?: string;
    to_date?: string;
    limit?: number;
    offset?: number;
  }) {
    return apiRequest<Paginated<AccessLog>>(`/admin/access-logs${buildQuery(params ?? {})}`, "GET");
  },

  listPlans(activeOnly = false) {
    return apiRequest<{ items: AdminPlan[]; total: number }>(
      `/admin/plans${buildQuery({ active_only: activeOnly ? "true" : undefined })}`,
      "GET",
    );
  },

  createPlan(payload: Partial<AdminPlan> & { code: string; name: string }) {
    return apiRequest<AdminPlan>("/admin/plans", "POST", payload);
  },

  updatePlan(planId: string, payload: Partial<AdminPlan>) {
    return apiRequest<AdminPlan>(`/admin/plans/${planId}`, "PATCH", payload);
  },

  deletePlan(planId: string) {
    return apiRequest<{ message: string }>(`/admin/plans/${planId}`, "DELETE");
  },

  listSubscriptions(params?: {
    user_id?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }) {
    return apiRequest<Paginated<AdminUserSubscription>>(
      `/admin/subscriptions${buildQuery(params ?? {})}`,
      "GET",
    );
  },

  assignSubscription(payload: {
    user_id: string;
    plan_id: string;
    status?: string;
    ends_at?: string;
  }) {
    return apiRequest<AdminUserSubscription>("/admin/subscriptions", "POST", payload);
  },

  updateSubscription(subscriptionId: string, payload: { status: string }) {
    return apiRequest<AdminUserSubscription>(`/admin/subscriptions/${subscriptionId}`, "PATCH", payload);
  },

  listPayments(params?: { status?: string; user_id?: string; limit?: number; offset?: number }) {
    return apiRequest<Paginated<AdminPayment>>(`/admin/payments${buildQuery(params ?? {})}`, "GET");
  },

  listCustomers(params?: { limit?: number; offset?: number }) {
    return apiRequest<Paginated<AdminCustomer>>(
      `/admin/customers${buildQuery(params ?? {})}`,
      "GET",
    );
  },

  syncPlansCatalog() {
    return apiRequest<{ created: number; updated: number; items: AdminPlan[]; total: number }>(
      "/admin/plans/sync-catalog",
      "POST",
    );
  },

  getPricingPromotion() {
    return apiRequest<{ active: boolean; discount_pct?: number; ends_at?: string | null }>(
      "/admin/commercial/promotion",
      "GET",
    );
  },

  getPricingPromotionOverview() {
    return apiRequest<AdminPromotionOverview>("/admin/commercial/promotion/overview", "GET");
  },

  activatePricingPromotion(durationMonths: 3 | 4 | 5 | 6) {
    return apiRequest<AdminPromotionOverview>("/admin/commercial/promotion/activate", "POST", {
      duration_months: durationMonths,
    });
  },

  deactivatePricingPromotion() {
    return apiRequest<AdminPromotionOverview>("/admin/commercial/promotion/deactivate", "POST");
  },

  listScrapingSources() {
    return apiRequest<{ items: ScrapingSource[]; total: number }>("/admin/scraping-sources", "GET");
  },

  createScrapingSource(payload: {
    code: string;
    name: string;
    base_url: string;
    description?: string;
    country?: string;
    is_active?: boolean;
  }) {
    return apiRequest<ScrapingSource>("/admin/scraping-sources", "POST", payload);
  },

  updateScrapingSource(id: string, payload: Partial<ScrapingSource>) {
    return apiRequest<ScrapingSource>(`/admin/scraping-sources/${id}`, "PATCH", payload);
  },

  deleteScrapingSource(id: string) {
    return apiRequest<{ message: string }>(`/admin/scraping-sources/${id}`, "DELETE");
  },

  listIntegrations() {
    return apiRequest<{ items: IntegrationSetting[]; total: number }>("/admin/integrations", "GET");
  },

  updateIntegration(key: string, payload: { settings: Record<string, unknown>; is_active?: boolean }) {
    return apiRequest<IntegrationSetting>(`/admin/integrations/${key}`, "PATCH", payload);
  },

  testIntegration(key: string) {
    return apiRequest<{ success: boolean; message: string }>(`/admin/integrations/${key}/test`, "POST");
  },

  listBudgetTemplates() {
    return apiRequest<{ items: BudgetTemplate[]; total: number }>("/admin/budget-templates", "GET");
  },

  setDefaultTemplate(id: string) {
    return apiRequest<BudgetTemplate>(`/admin/budget-templates/${id}/set-default`, "POST");
  },

  deleteBudgetTemplate(id: string) {
    return apiRequest<{ message: string }>(`/admin/budget-templates/${id}`, "DELETE");
  },

  auditTrail(params?: {
    limit?: number;
    offset?: number;
    project_id?: string;
    entity_type?: string;
    action?: string;
  }) {
    return apiRequest<Paginated<AuditTrailEntry>>(`/admin/audit-trail${buildQuery(params ?? {})}`, "GET");
  },
};
