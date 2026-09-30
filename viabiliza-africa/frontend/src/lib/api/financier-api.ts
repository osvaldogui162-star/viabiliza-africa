import { apiRequest } from "@/lib/api/http-client";
import type {
  FinancierDashboardResponse,
  FinancierMonitoringResponse,
  FinancierPortfolioResponse,
  FinancingListItem,
} from "@/lib/types/financier";

export const financierApi = {
  dashboard() {
    return apiRequest<FinancierDashboardResponse>("/financier/dashboard", "GET");
  },

  portfolio() {
    return apiRequest<FinancierPortfolioResponse>("/financier/portfolio", "GET");
  },

  alerts() {
    return apiRequest<{ items: import("@/lib/types/financier").FinancierAlert[]; total: number }>(
      "/financier/alerts",
      "GET",
    );
  },

  disbursements() {
    return apiRequest<{ items: import("@/lib/types/financier").FinancierDisbursement[]; total: number }>(
      "/financier/disbursements",
      "GET",
    );
  },

  documents() {
    return apiRequest<{ items: import("@/lib/types/financier").FinancierDocument[]; total: number }>(
      "/financier/documents",
      "GET",
    );
  },

  activity(limit = 50) {
    return apiRequest<{ items: import("@/lib/types/financier").FinancierActivityItem[]; total: number }>(
      `/financier/activity?limit=${limit}`,
      "GET",
    );
  },

  portfolioReport() {
    return apiRequest<{ rows: Record<string, unknown>[]; summary: unknown }>(
      "/financier/reports/portfolio",
      "GET",
    );
  },

  creditReport() {
    return apiRequest<{
      report_type: string;
      report_title: string;
      generated_at: string;
      rows: Record<string, unknown>[];
      summary: Record<string, unknown>;
    }>("/financier/reports/credit", "GET");
  },

  monitoring(financingId: string) {
    return apiRequest<FinancierMonitoringResponse>(`/financier/monitoring/${financingId}`, "GET");
  },

  billingIntegrations() {
    return apiRequest<{
      items: import("@/lib/types/financier").FinancierBillingIntegrationItem[];
      total: number;
      connected_count: number;
    }>("/financier/billing-integrations", "GET");
  },

  listProjectFinancing(projectId: string) {
    return apiRequest<{ items: FinancingListItem[]; total: number }>(
      `/projects/${projectId}/financing`,
      "GET",
    );
  },

  pendingApprovals() {
    return apiRequest<{ items: FinancingListItem[]; total: number }>(
      "/financier/pending-approvals",
      "GET",
    );
  },

  decideFinancing(
    financingId: string,
    payload: {
      decision: "approved" | "conditional" | "rejected";
      approved_amount?: string;
      disbursed_amount?: string;
      interest_rate_pct?: string;
      term_months?: number;
      notes?: string;
    },
  ) {
    return apiRequest<FinancingListItem>(`/financier/financing/${financingId}/decision`, "PATCH", payload);
  },

  createProjectFinancing(
    projectId: string,
    payload: {
      bank_code: string;
      decision?: "pending" | "approved" | "conditional" | "rejected";
      approved_amount: string;
      currency?: string;
      disbursed_amount?: string;
      interest_rate_pct?: string;
      term_months?: number;
      notes?: string;
    },
  ) {
    return apiRequest<FinancingListItem>(`/projects/${projectId}/financing`, "POST", payload);
  },

  createDisbursement(
    financingId: string,
    payload: { requested_amount: string; purpose?: string },
  ) {
    return apiRequest(`/financier/financing/${financingId}/disbursements`, "POST", payload);
  },

  updateDisbursement(
    disbursementId: string,
    payload: { status: string; approved_amount?: string; notes?: string },
  ) {
    return apiRequest(`/financier/disbursements/${disbursementId}`, "PATCH", payload);
  },

  createDocument(
    financingId: string,
    payload: { doc_type: string; title: string; file_ref?: string },
  ) {
    return apiRequest(`/financier/financing/${financingId}/documents`, "POST", payload);
  },

  validateDocument(
    documentId: string,
    payload: { validation_status: "valid" | "rejected"; notes?: string },
  ) {
    return apiRequest(`/financier/documents/${documentId}`, "PATCH", payload);
  },
};
