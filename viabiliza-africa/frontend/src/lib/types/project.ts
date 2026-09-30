export interface OwnerSummary {

  id: string;

  email: string;

  full_name: string;

}



export interface Project {

  id: string;

  owner_id: string;

  owner: OwnerSummary | null;

  name: string;

  description: string | null;

  company_name: string;

  company_tax_id: string | null;

  sector: string;

  sector_label: string;

  country: string;

  country_label: string;

  currency: string;

  investment_amount: string;

  project_horizon_years: number;

  discount_rate: string | null;

  status: string;

  status_label: string;

  has_approved_budget: boolean;

  is_owner: boolean;

  is_shared: boolean;

  my_access?: {
    permission: string;
    job_title?: string | null;
    effective_capabilities: Record<string, boolean>;
  } | null;

  shares_count: number;

  created_at: string;

  updated_at: string;

  bank_code?: string | null;

  bank_rate_label?: string | null;

  bank_rate_source_url?: string | null;

  rep_full_name?: string | null;

  rep_email?: string | null;

  rep_id_number?: string | null;

  rep_phone?: string | null;

  rep_role?: string | null;

  company_province?: string | null;

  company_province_label?: string | null;

  company_municipality?: string | null;

  company_municipality_label?: string | null;

  company_address?: string | null;

  company_activity?: string | null;

  company_phone?: string | null;

  company_email?: string | null;

  company_website?: string | null;

  company_latitude?: string | null;

  company_longitude?: string | null;

  geocode_verified?: boolean;

  geocode_source?: string | null;

  financing_type?: string | null;

  financing_type_label?: string | null;

  loan_term_months?: number | null;

  bank_branch?: string | null;

  /** Soma automática de todas as saídas (cost items) */

  spent_total?: string;

  /** Saldo disponível = investimento − saídas */

  remaining_balance?: string;

  capex_spent?: string;

  opex_spent?: string;

  mission?: string | null;
  vision?: string | null;
  core_values?: string[];
  swot_analysis?: SwotAnalysis;
  risk_register?: RiskItem[];
  aipex_incentives?: AipexIncentive[];
  strategic_generated_at?: string | null;
}

export interface SwotAnalysis {
  strengths?: string[];
  weaknesses?: string[];
  opportunities?: string[];
  threats?: string[];
}

export interface RiskItem {
  code: string;
  title: string;
  severity: string;
  mitigation: string;
}

export interface AipexIncentive {
  code: string;
  title: string;
  description: string;
  benefit_type: string;
}

export interface ExtractedCompanyFields {
  nif: string | null;
  company_name: string | null;
  email: string | null;
  phone: string | null;
  address: string | null;
  activity: string | null;
  text_preview?: string;
  fields_found?: number;
}



export interface ProjectShare {

  id: string;

  project_id: string;

  user_id: string;

  user_email: string;

  user_full_name: string;

  user_role: string;

  shared_by: string;

  shared_by_name: string;

  permission: string;

  created_at: string;

}



export interface PaginatedProjects {

  items: Project[];

  total: number;

  limit: number;

  offset: number;

}



export interface MetadataOption {

  value: string;

  label: string;

  website?: string;

  logo?: string;

  latitude?: number;

  longitude?: number;

}



export interface ProjectMetadata {

  sectors: MetadataOption[];

  countries: MetadataOption[];

  currencies: MetadataOption[];

  statuses: MetadataOption[];

  share_permissions: MetadataOption[];

  banks: MetadataOption[];

  provinces: MetadataOption[];

  financing_types: MetadataOption[];

}



export interface CreateProjectPayload {

  name: string;

  description?: string;

  company_name: string;

  company_tax_id?: string;

  sector: string;

  country: string;

  currency: string;

  investment_amount: string;

  project_horizon_years?: number;

  discount_rate?: string;

  bank_code?: string;

  bank_rate_label?: string;

  bank_rate_source_url?: string;

  rep_full_name: string;

  rep_email: string;

  rep_id_number: string;

  rep_phone: string;

  rep_role?: string;

  company_province: string;

  company_municipality: string;

  company_address?: string;

  company_activity?: string;

  company_phone?: string;

  company_email?: string;

  company_website?: string;

  company_latitude?: string;

  company_longitude?: string;

  geocode_verified?: boolean;

  geocode_source?: string;

  financing_type?: string;

  loan_term_months?: number;

  bank_branch?: string;

}



export type UpdateProjectPayload = Partial<CreateProjectPayload>;



export interface CompanyNifLookup {

  nif: string;

  company_name: string;

  address: string | null;

  activity: string | null;

  status: string | null;

  source_url: string;

  fields: Record<string, string>;

}



export interface BankDiscountRate {

  bank_code: string;

  bank_name: string;

  discount_rate: string;

  product_label: string;

  source_url: string;

  currency: string;

}



export interface BankBranchOption {

  value: string;

  label: string;

  province: string;

  municipality: string;

  address: string;

  description: string;

}



export interface BankBranchesResponse {

  bank_code: string;

  items: BankBranchOption[];

  total: number;

}



export interface GeocodeResult {

  latitude: string;

  longitude: string;

  formatted_address: string;

  source: string;

  verified: boolean;

}



export interface AngolaValidationResult {

  valid: boolean;

  message: string;

  source: string;

  operator?: string | null;

  normalized_value?: string | null;

}



export interface MunicipalitiesResponse {

  municipalities: MetadataOption[];

}

