import { apiBlob, apiRequest } from "@/lib/api/http-client";

import type {
  AnalysesListResponse,
  BenchmarksResponse,
  FinancialAnalysis,
  MonteCarloResult,
  ScenarioAnalysisResult,
  SensitivityResult,
} from "@/lib/types/analysis";

export const analysisApi = {
  calculateIndicators(projectId: string, assumptions?: Record<string, string | null>) {
    return apiRequest<FinancialAnalysis>(`/projects/${projectId}/analysis/indicators`, "POST", {
      assumptions,
    });
  },

  listAnalyses(projectId: string, limit = 20) {
    return apiRequest<AnalysesListResponse>(
      `/projects/${projectId}/analysis/indicators?limit=${limit}`,
      "GET",
    );
  },

  getAnalysis(projectId: string, analysisId: string) {
    return apiRequest<FinancialAnalysis>(
      `/projects/${projectId}/analysis/indicators/${analysisId}`,
      "GET",
    );
  },

  exportIndicators(projectId: string, analysisId?: string, language = "pt") {
    const params = new URLSearchParams();
    if (analysisId) params.set("analysis_id", analysisId);
    if (language) params.set("lang", language);
    const qs = params.toString() ? `?${params.toString()}` : "";
    return apiBlob(`/projects/${projectId}/analysis/indicators/export${qs}`);
  },

  runMonteCarlo(
    projectId: string,
    payload: { iterations?: number; analysis_id?: string; variable_std_devs?: Record<string, number> },
  ) {
    return apiRequest<MonteCarloResult>(`/projects/${projectId}/analysis/monte-carlo`, "POST", payload);
  },

  listMonteCarlo(projectId: string) {
    return apiRequest<{ items: MonteCarloResult[]; total: number }>(
      `/projects/${projectId}/analysis/monte-carlo`,
      "GET",
    );
  },

  runSensitivity(
    projectId: string,
    payload?: {
      analysis_id?: string;
      variables?: Array<{
        key: string;
        label?: string;
        shock_low_pct?: number;
        shock_high_pct?: number;
        base_value?: number;
      }>;
    },
  ) {
    return apiRequest<SensitivityResult>(`/projects/${projectId}/analysis/sensitivity`, "POST", payload ?? {});
  },

  listSensitivity(projectId: string) {
    return apiRequest<{ items: SensitivityResult[]; total: number }>(
      `/projects/${projectId}/analysis/sensitivity`,
      "GET",
    );
  },

  getBenchmarks(projectId: string) {
    return apiRequest<BenchmarksResponse>(`/projects/${projectId}/analysis/benchmarks`, "GET");
  },

  runScenarios(projectId: string) {
    return apiRequest<ScenarioAnalysisResult>(`/projects/${projectId}/analysis/scenarios`, "POST", {});
  },
};
