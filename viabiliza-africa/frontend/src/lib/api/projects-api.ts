import { apiBlob, apiRequest, apiUpload, buildQuery } from "@/lib/api/http-client";
import type {
  BankBranchesResponse,
  BankDiscountRate,
  CompanyNifLookup,
  CreateProjectPayload,
  ExtractedCompanyFields,
  GeocodeResult,
  AngolaValidationResult,
  MunicipalitiesResponse,
  PaginatedProjects,
  Project,
  ProjectMetadata,
  ProjectShare,
  UpdateProjectPayload,
} from "@/lib/types/project";

interface ProjectDetailResponse {
  project: Project;
  shares: ProjectShare[];
}

let metadataRequest: Promise<ProjectMetadata> | null = null;
const inflightListRequests = new Map<string, Promise<PaginatedProjects>>();

export function resetProjectsApiCaches() {
  inflightListRequests.clear();
  metadataRequest = null;
}

export const projectsApi = {
  metadata() {
    if (!metadataRequest) {
      metadataRequest = apiRequest<ProjectMetadata>("/projects/metadata", "GET").catch((err) => {
        metadataRequest = null;
        throw err;
      });
    }
    return metadataRequest;
  },

  municipalities(province: string) {
    return apiRequest<MunicipalitiesResponse>(
      `/projects/metadata/municipalities${buildQuery({ province })}`,
      "GET",
    );
  },

  geocode(payload: { province: string; municipality: string; address?: string }) {
    return apiRequest<GeocodeResult>("/projects/geocode", "POST", payload);
  },

  validateBi(bi: string) {
    return apiRequest<AngolaValidationResult>(
      `/validate/bi/${encodeURIComponent(bi)}`,
      "GET",
    );
  },

  validatePhone(phone: string, optional = false) {
    return apiRequest<AngolaValidationResult>(
      `/validate/phone/${encodeURIComponent(phone)}${optional ? "?optional=true" : ""}`,
      "GET",
    );
  },

  list(params?: {
    status?: string;
    country?: string;
    sector?: string;
    search?: string;
    limit?: number;
    offset?: number;
  }) {
    const query = buildQuery(params ?? {});
    const cacheKey = query || "default";
    const existing = inflightListRequests.get(cacheKey);
    if (existing) return existing;

    const request = apiRequest<PaginatedProjects>(`/projects${query}`, "GET").finally(() => {
      inflightListRequests.delete(cacheKey);
    });
    inflightListRequests.set(cacheKey, request);
    return request;
  },

  get(id: string) {
    return apiRequest<ProjectDetailResponse>(`/projects/${id}`, "GET").then((data) => data.project);
  },

  create(payload: CreateProjectPayload) {
    return apiRequest<Project>("/projects", "POST", payload);
  },

  update(id: string, payload: UpdateProjectPayload) {
    return apiRequest<Project>(`/projects/${id}`, "PATCH", payload);
  },

  delete(id: string) {
    return apiRequest<{ message: string }>(`/projects/${id}`, "DELETE");
  },

  listShares(id: string) {
    return apiRequest<{ items: ProjectShare[]; total: number }>(`/projects/${id}/shares`, "GET");
  },

  share(id: string, userEmail: string, permission = "view") {
    return apiRequest<
      ProjectShare | {
        pending_invite: boolean;
        invite_email?: string;
        message?: string;
        expires_at?: string;
      }
    >(`/projects/${id}/shares`, "POST", {
      user_email: userEmail,
      permission,
    });
  },

  removeShare(projectId: string, userId: string) {
    return apiRequest<{ message: string }>(`/projects/${projectId}/shares/${userId}`, "DELETE");
  },

  lookupNif(nif: string) {
    return apiRequest<CompanyNifLookup>(`/companies/nif/${encodeURIComponent(nif)}`, "GET");
  },

  extractCompanyDocument(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    return apiUpload<{ extracted: ExtractedCompanyFields; filename: string }>(
      "/companies/extract-document",
      formData,
    );
  },

  generateStrategicInsights(projectId: string) {
    return apiRequest<{
      project_id: string;
      generated_at: string;
      mission: string;
      vision: string;
      core_values: string[];
      swot_analysis: Record<string, string[]>;
      risk_register: Array<Record<string, string>>;
      aipex_incentives: Array<Record<string, string>>;
    }>(`/projects/${projectId}/strategic-insights`, "POST", {});
  },

  getSectorProfile(projectId: string, lang: "pt" | "en" = "pt") {
    return apiRequest<import("@/lib/types/sector-profile").SectorProfile>(
      `/projects/${projectId}/sector-profile${buildQuery({ lang })}`,
      "GET",
    );
  },

  getBankDiscountRate(bankCode: string, sector?: string) {
    return apiRequest<BankDiscountRate>(
      `/banks/${bankCode}/discount-rate${buildQuery({ sector })}`,
      "GET",
    );
  },

  getBankBranches(bankCode: string, province?: string) {
    return apiRequest<BankBranchesResponse>(
      `/banks/${bankCode}/branches${buildQuery({ province })}`,
      "GET",
    );
  },

  getBillingIntegration(projectId: string) {
    return apiRequest<{
      integration: {
        erp_label: string | null;
        connection_status: string;
        last_sync_at: string | null;
        last_hash: string | null;
        api_key_hint: string | null;
        has_api_key: boolean;
        sync_endpoint: string;
        sync_header: string;
      } | null;
      sync_endpoint: string;
      sync_header: string;
      steps: { step: number; code: string; label_pt: string; done: boolean }[];
    }>(`/projects/${projectId}/billing-integration`, "GET");
  },

  configureBillingIntegration(projectId: string, erp_label: string) {
    return apiRequest<{
      api_key?: string;
      api_key_show_once?: boolean;
      integration: Record<string, unknown>;
    }>(`/projects/${projectId}/billing-integration`, "POST", { erp_label });
  },

  regenerateBillingApiKey(projectId: string) {
    return apiRequest<{ api_key: string; api_key_show_once?: boolean }>(
      `/projects/${projectId}/billing-integration/regenerate-key`,
      "POST",
      {},
    );
  },

  syncBillingIntegration(projectId: string, payload: Record<string, unknown>) {
    return apiRequest(`/projects/${projectId}/billing-integration/sync`, "POST", { payload });
  },
};

export { apiBlob };
