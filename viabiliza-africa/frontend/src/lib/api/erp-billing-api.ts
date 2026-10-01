import { apiRequest } from "@/lib/api/http-client";

export interface ErpProviderField {
  key: string;
  label_pt: string;
  required?: boolean;
  secret?: boolean;
  default?: string;
}

export interface ErpProvider {
  code: string;
  name: string;
  regions: string[];
  integration: string;
  agt_certified: boolean;
  free_tier: boolean;
  notes_pt: string;
  notes_en: string;
  config_fields: ErpProviderField[];
}

export interface ErpBillingConnection {
  provider_code: string;
  connection_status: string;
  auto_fiscal_on_payment: boolean;
  config: Record<string, string>;
  last_test_at?: string | null;
  last_error?: string | null;
  updated_at?: string;
}

export interface FiscalDocumentRow {
  id: string;
  payment_id?: string | null;
  provider_code: string;
  status: string;
  external_ref?: string | null;
  has_agt_export: boolean;
  error_message?: string | null;
  issued_at?: string | null;
  created_at?: string;
}

export const erpBillingApi = {
  listProviders() {
    return apiRequest<{ items: ErpProvider[]; total: number }>("/erp-billing/providers", "GET");
  },

  getMine() {
    return apiRequest<{ connection: ErpBillingConnection | null; fiscal_documents: FiscalDocumentRow[] }>(
      "/me/erp-billing",
      "GET",
    );
  },

  save(payload: {
    provider_code: string;
    config: Record<string, string>;
    auto_fiscal_on_payment?: boolean;
  }) {
    return apiRequest<{ connection: ErpBillingConnection }>("/me/erp-billing", "PUT", payload);
  },

  test(payload?: { provider_code?: string; config?: Record<string, string> }) {
    return apiRequest<{ ok: boolean; connection: ErpBillingConnection }>(
      "/me/erp-billing/test",
      "POST",
      payload ?? {},
    );
  },

  agtExportUrl(documentId: string) {
    const base = (process.env.NEXT_PUBLIC_API_BASE_URL?.trim() || "/api/v1").replace(/\/$/, "");
    return `${base}/me/erp-billing/fiscal-documents/${documentId}/agt-export`;
  },
};
