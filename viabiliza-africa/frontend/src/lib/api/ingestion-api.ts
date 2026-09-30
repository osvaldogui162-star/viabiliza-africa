import { apiRequest, apiUpload } from "@/lib/api/http-client";
import type {
  AuditTrailEntry,
  AutoIngestionPreview,
  AutoIngestionResult,
  Budget,
  BudgetsResponse,
  BudgetVerification,
  CostItem,
  CostItemsResponse,
  ProformaInvoice,
  ProformasResponse,
  ReportVerification,
  ScrapingJobResponse,
  ScrapingSourcesResponse,
} from "@/lib/types/ingestion";

export const ingestionApi = {
  listScrapingSources() {
    return apiRequest<ScrapingSourcesResponse>("/projects/scraping/sources", "GET");
  },

  listCostItems(projectId: string, itemType?: string) {
    const qs = itemType ? `?item_type=${itemType}` : "";
    return apiRequest<CostItemsResponse>(`/projects/${projectId}/cost-items${qs}`, "GET");
  },

  createCostItem(
    projectId: string,
    payload: {
      item_type: string;
      category: string;
      description: string;
      quantity: string;
      unit?: string;
      unit_price: string;
      supplier_nif?: string;
      supplier_name?: string;
    },
  ) {
    return apiRequest<CostItem>(`/projects/${projectId}/cost-items`, "POST", payload);
  },

  importExcel(projectId: string, file: File) {
    const formData = new FormData();
    formData.append("file", file);
    return apiUpload<{ imported: number; items: CostItem[] }>(
      `/projects/${projectId}/cost-items/import/excel`,
      formData,
    );
  },

  deleteCostItem(projectId: string, itemId: string) {
    return apiRequest<{ message: string }>(
      `/projects/${projectId}/cost-items/${itemId}`,
      "DELETE",
    );
  },

  updateCostItem(
    projectId: string,
    itemId: string,
    payload: {
      category?: string;
      description?: string;
      quantity?: string;
      unit?: string;
      unit_price?: string;
    },
  ) {
    return apiRequest<CostItem>(
      `/projects/${projectId}/cost-items/${itemId}`,
      "PATCH",
      payload,
    );
  },

  previewAutoIngestion(projectId: string) {
    return apiRequest<AutoIngestionPreview>(
      `/projects/${projectId}/ingestion/auto/preview`,
      "GET",
    );
  },

  runAutoIngestion(
    projectId: string,
    payload?: {
      sources?: string[];
      replace_existing?: boolean;
      generate_proforma?: boolean;
      items?: Array<{ key: string; quantity: string; include?: boolean }>;
    },
  ) {
    return apiRequest<AutoIngestionResult>(
      `/projects/${projectId}/ingestion/auto/run`,
      "POST",
      payload ?? { replace_existing: false, generate_proforma: true },
    );
  },

  startScraping(projectId: string, searchQuery: string, sources?: string[]) {
    return apiRequest<ScrapingJobResponse>(`/projects/${projectId}/scraping/jobs`, "POST", {
      search_query: searchQuery,
      sources: sources?.length ? sources : undefined,
    });
  },

  getScrapingJob(projectId: string, jobId: string) {
    return apiRequest<ScrapingJobResponse>(
      `/projects/${projectId}/scraping/jobs/${jobId}`,
      "GET",
    );
  },

  selectScrapingResult(
    projectId: string,
    resultId: string,
    payload?: { item_type?: string; category?: string; quantity?: string },
  ) {
    return apiRequest<CostItem>(
      `/projects/${projectId}/scraping/results/${resultId}/select`,
      "POST",
      payload ?? {},
    );
  },

  listBudgets(projectId: string) {
    return apiRequest<BudgetsResponse>(`/projects/${projectId}/budgets`, "GET");
  },

  generateBudget(projectId: string) {
    return apiRequest<Budget>(`/projects/${projectId}/budgets`, "POST", {});
  },

  approveBudget(projectId: string, budgetId: string) {
    return apiRequest<Budget>(`/projects/${projectId}/budgets/${budgetId}/approve`, "POST", {});
  },

  generateProforma(
    projectId: string,
    budgetId: string,
    payload?: { client_name?: string; client_tax_id?: string; notes?: string },
  ) {
    return apiRequest<ProformaInvoice>(
      `/projects/${projectId}/budgets/${budgetId}/proforma`,
      "POST",
      payload ?? {},
    );
  },

  listProformas(projectId: string) {
    return apiRequest<ProformasResponse>(`/projects/${projectId}/proformas`, "GET");
  },

  getAuditTrail(projectId: string) {
    return apiRequest<{ items: AuditTrailEntry[]; total: number }>(
      `/projects/${projectId}/audit-trail`,
      "GET",
    );
  },
};

function publicApiBase(): string {
  // Preferir proxy same-origin (/api/v1) — funciona com qualquer IP do frontend
  const configured = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (configured) return configured.replace(/\/$/, "");
  if (typeof window !== "undefined") return "/api/v1";
  return "http://127.0.0.1:5000/api/v1";
}

export function verifyBudgetPublic(hash: string, signal?: AbortSignal) {
  const base = publicApiBase();
  return fetch(`${base}/verify/budget/${encodeURIComponent(hash)}`, {
    cache: "no-store",
    signal,
  }).then(async (response) => {
    const data = (await response.json().catch(() => ({}))) as BudgetVerification & {
      error?: { message?: string };
    };
    if (!response.ok || data.valid === false) {
      throw new Error(data.message ?? data.error?.message ?? "Orçamento não encontrado ou foi alterado");
    }
    return data;
  });
}

export function verifyReportPublic(hash: string) {
  const base = publicApiBase();
  return fetch(`${base}/verify/report/${encodeURIComponent(hash)}`, {
    cache: "no-store",
  }).then(async (response) => {
    const data = (await response.json().catch(() => ({}))) as ReportVerification & {
      error?: { message?: string };
    };
    if (!response.ok || data.valid === false) {
      throw new Error(data.message ?? data.error?.message ?? "Relatório não encontrado ou foi alterado");
    }
    return data;
  });
}
