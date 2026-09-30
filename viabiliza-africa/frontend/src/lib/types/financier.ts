export type MonitoringStatus = "on_track" | "attention" | "critical";

export type FinancingDecision = "pending" | "approved" | "conditional" | "rejected";

export type FinancingWorkflowStatus = "pending_bank" | "active" | "rejected" | "closed";

export type ScheduleStatus = "on_time" | "delayed" | "stalled" | "unknown";

export type TerminalRiskLevel = "low" | "medium" | "high";

export type BillingConnectionStatus =
  | "pending"
  | "integrating"
  | "authenticated"
  | "syncing"
  | "active"
  | "error"
  | "disconnected";

export interface TerminalIndicatorRow {
  category: string;
  key: string;
  label_pt: string;
  label_en: string;
  unit: string;
  forecast: string;
  real: string | null;
  deviation: number | null;
  deviation_kind: "pct" | "pp";
  status: string;
}

export interface TerminalMonitoringPanel {
  brand: string;
  billing: {
    connected: boolean;
    status: BillingConnectionStatus | string;
    erp_label: string | null;
    last_sync_at: string | null;
    last_hash: string | null;
    api_key_hint: string | null;
    steps: { step: number; code: string; label_pt: string; done: boolean }[];
  };
  indicators: TerminalIndicatorRow[];
  alerts: FinancierAlert[];
  risk_level: TerminalRiskLevel;
  deviation_pct: number | null;
  liquidity_index: number | null;
  trends: { revenue: string; margin: string; cash: string };
  recommendations: string[];
  risk_score?: { value: number; level: TerminalRiskLevel };
}

export interface FinancierBillingIntegrationItem {
  financing_id: string;
  project_id: string;
  project_name: string;
  company_name: string | null;
  integration: {
    project_id: string;
    erp_label: string | null;
    connection_status: BillingConnectionStatus;
    api_key_hint: string | null;
    last_sync_at: string | null;
    last_hash: string | null;
    latest_snapshot: Record<string, unknown>;
  } | null;
  steps: { step: number; code: string; label_pt: string; done: boolean }[];
}

export interface BankBrand {
  code: string;
  label_pt: string;
  label_en: string;
  logo_path: string | null;
  website?: string;
}

export interface FinancingListItem {
  id: string;
  project_id: string;
  project_name: string;
  company_name: string | null;
  sector: string;
  bank: BankBrand;
  decision: FinancingDecision;
  workflow_status: FinancingWorkflowStatus;
  approved_amount: string;
  currency: string;
  disbursed_amount: string;
  monitoring_status: MonitoringStatus;
  decision_at: string;
  submitted_at?: string;
  bank_decided_at?: string | null;
  notes?: string | null;
  spent_total?: string;
  utilization_pct?: number;
  physical_pct?: number;
  schedule_status?: ScheduleStatus;
  project_status?: string;
  pending_count?: number;
  schedule?: {
    tasks_total: number;
    tasks_done: number;
    tasks_overdue: number;
  };
  deviation_pct?: number | null;
  risk_level?: TerminalRiskLevel;
  billing_status?: "connected" | "pending" | "disconnected";
  billing_connected?: boolean;
}

export interface FinancierPortfolioResponse {
  items: FinancingListItem[];
  total: number;
  stats: {
    on_track: number;
    attention: number;
    critical: number;
    total_exposure: string;
  };
  viewer_bank: BankBrand | null;
}

export interface FinancierAlert {
  type: string;
  severity: string;
  code: string;
  message_pt: string;
  financing_id?: string;
  project_id?: string;
  project_name?: string;
}

export interface DashboardCharts {
  bar_comparison: ChartSlice[];
  risk_donut: ChartSlice[];
  spend_trend: { month: string; amount: number }[];
  project_comparison: {
    financing_id: string;
    name: string;
    financial_pct: number;
    physical_pct: number;
    approved: string;
  }[];
  gauge: { value: number; max: number; label_pt: string; label_en: string };
  physical_vs_financial: { avg_financial_pct: number; avg_physical_pct: number };
}

export interface FinancierDashboardResponse {
  charts?: DashboardCharts;
  sections: {
    carteira: { projects_count: number; total_exposure: string; currency: string };
    exposicao: { total_approved: string; by_risk: Record<string, number> };
    desembolsos: {
      total_disbursed: string;
      disbursement_vs_approved_pct: number;
      pending_requests: number;
    };
    execucao: {
      total_executed: string;
      execution_vs_approved_pct: number;
      avg_physical_pct: number;
    };
    risco: Record<string, number>;
    pendencias: { alerts_count: number; top: FinancierAlert[] };
    aprovacoes_pendentes?: { count: number; items: FinancingListItem[] };
    terminal?: {
      billing_connected_count: number;
      billing_required_count: number;
      avg_deviation_pct: number | null;
      risk_mix: Record<string, number>;
    };
  };
  pending_approvals?: FinancingListItem[];
  items: FinancingListItem[];
  total: number;
  stats: FinancierPortfolioResponse["stats"];
  viewer_bank: BankBrand | null;
  recent_activity: FinancierActivityItem[];
}

export interface FinancierActivityItem {
  id: string;
  action: string;
  summary: string;
  actor_name: string | null;
  project_id: string | null;
  financing_id: string | null;
  created_at: string;
}

export interface FinancierDisbursement {
  id: string;
  financing_id: string;
  project_id?: string;
  project_name?: string;
  requested_amount: string;
  approved_amount: string | null;
  paid_amount: string;
  currency: string;
  status: string;
  purpose: string | null;
  requested_at: string;
  decided_at: string | null;
  paid_at: string | null;
  notes: string | null;
}

export interface FinancierDocument {
  id: string;
  financing_id: string;
  project_id?: string;
  project_name?: string;
  doc_type: string;
  title: string;
  file_ref: string | null;
  validation_status: string;
  created_at: string;
}

export interface ChartSlice {
  label: string;
  value: number;
  color: string;
}

export interface FinancierMonitoringWorkflow {
  status: FinancingWorkflowStatus;
  awaiting_bank_decision: boolean;
  can_decide: boolean;
}

export interface FinancierMonitoringResponse {
  financing: FinancingListItem;
  workflow?: FinancierMonitoringWorkflow;
  project: {
    id: string;
    name: string;
    company_name: string | null;
    sector_label: string;
    status: string;
    updated_at: string;
    province?: string | null;
    investment_amount?: string;
  };
  monitoring_status: MonitoringStatus;
  charts?: {
    utilization_pct: number;
    execution_pct_of_investment: number;
    summary: {
      approved_amount: number;
      disbursed_amount: number;
      investment_amount: number;
      spent_total: number;
      remaining_budget: number;
      currency: string;
    };
    donut_execution: ChartSlice[];
    bar_comparison: ChartSlice[];
    gauge: { value: number; max: number; label_pt: string; label_en: string };
    spend_trend: { month: string; amount: number }[];
  };
  financial?: Record<string, unknown>;
  physical?: { progress_pct: number; tasks_summary: Record<string, unknown> };
  schedule?: { status: ScheduleStatus; milestones: unknown[] };
  alerts?: FinancierAlert[];
  disbursements?: FinancierDisbursement[];
  documents?: FinancierDocument[];
  activity?: FinancierActivityItem[];
  terminal?: TerminalMonitoringPanel | null;
}
