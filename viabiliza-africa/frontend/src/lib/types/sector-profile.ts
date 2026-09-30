export type UseCaseStatus = "automated" | "partial" | "planned";

export interface SectorUseCase {
  code: string;
  title: string;
  status: UseCaseStatus;
  business_rules: string[];
  outputs: string[];
}

export interface SectorModuleSummary {
  code: string;
  name: string;
  description: string;
  priority: string;
  sectors: string[];
  kpis: string[];
  certifications: string[];
  use_cases: SectorUseCase[];
}

export interface SectorBenchmark {
  key: string;
  label: string;
  value: number;
  unit: string;
}

export interface SectorProfile {
  project_id: string;
  project_name: string;
  sector: string;
  primary_module: SectorModuleSummary;
  esg_module: SectorModuleSummary;
  related_modules: SectorModuleSummary[];
  catalog: {
    items_count: number;
    items: Array<{
      key: string;
      item_type: string;
      category: string;
      description: string;
      quantity: string;
      unit: string;
    }>;
    has_more: boolean;
  };
  benchmarks: SectorBenchmark[];
  coverage: {
    automated: number;
    partial: number;
    planned: number;
    total_use_cases: number;
    catalog_items: number;
    benchmarks: number;
  };
  business_rules_summary: string[];
  recommended_certifications: string[];
}
