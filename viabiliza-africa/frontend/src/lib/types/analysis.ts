export interface IndicatorItem {
  key: string;
  label: string;
  value: number | string | null;
  unit: string;
  category?: string;
}

export interface FinancialIndicators {
  items?: IndicatorItem[];
  by_category?: Record<string, IndicatorItem[]>;
  summary?: Record<string, number | string | boolean | null>;
}

export interface FinancialAnalysis {
  id: string;
  project_id: string;
  status?: string;
  indicators: FinancialIndicators;
  assumptions: Record<string, string | null>;
  cash_flows?: CashFlowProjection;
  indicators_count?: number;
  calculation_hash?: string;
  created_at: string;
}

export interface CashFlowProjection {
  years: number[];
  revenue: number[];
  opex: number[];
  ebitda: number[];
  depreciation: number[];
  ebit: number[];
  interest: number[];
  ebt: number[];
  tax: number[];
  net_income: number[];
  free_cash_flow: number[];
  cumulative_fcf: number[];
}

export interface ScenarioResult {
  code: string;
  label: string;
  revenue_adjustment_pct: string;
  opex_adjustment_pct: string;
  npv: number;
  irr: number | null;
  payback_years: number | null;
  total_revenue: number;
  total_fcf: number;
}

export interface ScenarioAnalysisResult {
  project_id: string;
  investment: string;
  horizon_years: number;
  scenarios: ScenarioResult[];
}

export interface AnalysesListResponse {
  items: FinancialAnalysis[];
  total: number;
}

export interface MonteCarloStatistics {
  mean: number;
  std: number;
  min: number;
  max: number;
  median: number;
}

export interface MonteCarloPercentiles {
  p5: number;
  p25: number;
  p50: number;
  p75: number;
  p95: number;
}

export interface MonteCarloResults {
  statistics: MonteCarloStatistics;
  probability_npv_positive: number;
  percentiles: MonteCarloPercentiles;
}

export interface MonteCarloResult {
  id: string;
  project_id: string;
  iterations: number;
  parameters?: Record<string, unknown>;
  results: MonteCarloResults;
  created_at: string;
}

export interface SensitivityTornadoItem {
  key: string;
  label: string;
  low_npv?: number;
  high_npv?: number;
  base_npv?: number;
  impact: number;
  low_irr?: number | null;
  high_irr?: number | null;
  base_irr?: number | null;
}

export interface SensitivityResults {
  base_npv: number;
  base_irr: number | null;
  tornado_npv: SensitivityTornadoItem[];
  tornado_irr: SensitivityTornadoItem[];
}

export interface SensitivityResult {
  id: string;
  project_id: string;
  variables: { items?: Array<Record<string, unknown>> };
  results: SensitivityResults;
  created_at: string;
}

export interface BenchmarkComparison {
  metric_key: string;
  metric_label: string;
  indicator_key: string;
  benchmark_value: number;
  project_value: number | null;
  difference: number | null;
  unit: string;
  status: "above" | "below" | "equal" | "no_data";
  source: string;
}

export interface BenchmarksResponse {
  sector: string;
  country: string;
  has_analysis: boolean;
  comparisons: BenchmarkComparison[];
  total: number;
}
