export type ReportType = "international" | "bfa" | "bda";
export type ReportLanguage = "pt" | "en";

export interface Report {
  id: string;
  project_id: string;
  report_type: string;
  report_type_label: string;
  language: string;
  currency: string;
  title?: string;
  status: string;
  verification_hash?: string | null;
  hash?: string | null;
  qr_code_data?: string | null;
  qr_code_url?: string | null;
  file_size_bytes: number | null;
  created_at: string;
}

export interface ReportsListResponse {
  items: Report[];
  total: number;
}

export interface SendReportEmailResult {
  message: string;
  to: string;
  subject?: string;
  sent_at?: string;
  verification_hash?: string;
}
