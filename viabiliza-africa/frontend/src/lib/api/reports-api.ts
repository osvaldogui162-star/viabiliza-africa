import { apiBlob, apiRequest } from "@/lib/api/http-client";

import type {
  Report,
  ReportLanguage,
  ReportType,
  ReportsListResponse,
  SendReportEmailResult,
} from "@/lib/types/reports";

export const reportsApi = {
  list(projectId: string) {
    return apiRequest<ReportsListResponse>(`/projects/${projectId}/reports`, "GET");
  },

  generate(
    projectId: string,
    payload: {
      report_type: ReportType;
      language?: ReportLanguage;
      currency?: string;
      print_optimized?: boolean;
    },
  ) {
    return apiRequest<Report>(`/projects/${projectId}/reports`, "POST", payload);
  },

  get(projectId: string, reportId: string) {
    return apiRequest<Report>(`/projects/${projectId}/reports/${reportId}`, "GET");
  },

  download(projectId: string, reportId: string) {
    return apiBlob(`/projects/${projectId}/reports/${reportId}/download`);
  },

  print(projectId: string, reportId: string) {
    return apiBlob(`/projects/${projectId}/reports/${reportId}/print`);
  },

  sendEmail(
    projectId: string,
    reportId: string,
    payload: { to_email: string; subject?: string; message?: string },
  ) {
    return apiRequest<SendReportEmailResult>(
      `/projects/${projectId}/reports/${reportId}/send-email`,
      "POST",
      payload,
    );
  },

  shareWhatsApp(projectId: string, reportId: string, phone?: string) {
    return apiRequest<{
      message?: string;
      share_url?: string;
      whatsapp_url?: string;
      expires_at?: string;
    }>(`/projects/${projectId}/reports/${reportId}/share-whatsapp`, "POST", { phone });
  },

  submitToBank(projectId: string, reportId: string, bankCode: "bfa" | "bda") {
    return apiRequest<{ message: string; reference?: string; status?: string }>(
      `/projects/${projectId}/reports/${reportId}/submit-bank`,
      "POST",
      { bank_code: bankCode },
    );
  },
};
