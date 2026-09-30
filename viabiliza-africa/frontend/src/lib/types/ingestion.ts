export interface SupplierContact {
  code: string;
  name: string;
  email?: string | null;
  phone?: string | null;
  portal_url?: string | null;
  contact_page?: string | null;
}

export interface CostItem {
  id: string;
  project_id: string;
  item_type: string;
  category: string;
  description: string;
  quantity: string;
  unit: string;
  unit_price: string;
  total_amount: string;
  currency: string;
  supplier_name: string | null;
  supplier_nif?: string | null;
  supplier_url: string | null;
  source: string;
  /** Origem legível do preço (Jumia, Ovarmat, Referência setorial, …). */
  source_label?: string;
  /** Contactos/email/portal obtidos dos sites dos fornecedores. */
  contacts?: SupplierContact[];
  data_hash: string | null;
  metadata?: Record<string, unknown> | null;
  created_at: string;
}

export interface CostItemsResponse {
  items: CostItem[];
  total: number;
}

export interface Budget {
  id: string;
  project_id: string;
  budget_number: string;
  title: string;
  status: string;
  total_amount: string;
  currency: string;
  verification_hash: string | null;
  qr_code_data: string | null;
  qr_code_image: string | null;
  items_count: number;
  created_at: string;
  approved_at: string | null;
}

export interface BudgetsResponse {
  items: Budget[];
  total: number;
}

export interface ScrapingSource {
  id: string;
  code: string;
  name: string;
  base_url: string;
  is_active: boolean;
  categories?: string[];
  scrape_enabled?: boolean;
  city_note?: string | null;
}

export interface ScrapingSourcesResponse {
  items: ScrapingSource[];
  total: number;
}

export interface ScrapingJob {
  id: string;
  project_id: string;
  search_query: string;
  status: string;
  sources: string[];
  results_count: number;
  created_at: string;
  completed_at?: string | null;
}

export interface ScrapingResult {
  id: string;
  job_id: string;
  source: string;
  supplier_name: string;
  product_name: string;
  price: string;
  currency: string;
  product_url: string | null;
  is_selected: boolean;
  data_hash: string;
}

export interface ScrapingJobResponse {
  job: ScrapingJob;
  results: ScrapingResult[];
}

export interface AuditTrailEntry {
  id: string;
  project_id: string;
  action: string;
  entity_type: string;
  entity_id: string;
  actor_id: string | null;
  data_hash: string;
  previous_hash: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

export interface AutoCatalogItem {
  key: string;
  item_type: string;
  category: string;
  description: string;
  quantity: string;
  unit: string;
  search_query: string;
  pricing_mode: string;
  has_reference_price: boolean;
}

export interface AutoIngestionPreview {
  sector: string;
  project_name: string;
  currency: string;
  items: AutoCatalogItem[];
  total_items: number;
  sources_hint: string[];
  retail_suppliers_count?: number;
  retail_suppliers_sample?: string[];
}

export interface TransparencyLine {
  item_id: string;
  description: string;
  category: string;
  item_type: string;
  quantity: string;
  unit: string;
  unit_price: string;
  total_amount: string;
  currency: string;
  source: string;
  source_url?: string | null;
  product_name?: string | null;
  supplier_name?: string | null;
  selection_method?: string | null;
  from_marketplace: boolean;
}

export interface TransparencyDocument {
  title: string;
  project_id: string;
  project_name: string;
  sector: string;
  company_name: string;
  company_tax_id?: string | null;
  currency: string;
  sources_consulted: string[];
  methodology: string;
  lines: TransparencyLine[];
  totals: { capex: string; opex: string; grand_total: string };
  verification_hash: string;
  verify_url: string;
  next_steps: string[];
}

export interface AutoIngestionResult {
  items: CostItem[];
  items_count: number;
  budget: Budget;
  proforma: Record<string, unknown> | null;
  transparency_document: TransparencyDocument;
  scraping_job_id: string;
  sources_used: string[];
}

export interface ProformaInvoice {
  id: string;
  budget_id: string;
  project_id: string;
  invoice_number: string;
  client_name: string;
  client_tax_id: string | null;
  total_amount: string;
  currency: string;
  verification_hash: string;
  issued_at: string;
  qr_code_data: string | null;
  qr_code_image: string | null;
  verify_url?: string;
}

export interface ProformasResponse {
  items: ProformaInvoice[];
  total: number;
}

export interface BudgetVerificationItem {
  item_type: string;
  category: string;
  description: string;
  quantity: string;
  unit: string;
  unit_price: string;
  total_amount: string;
  item_hash: string;
  supplier_name: string | null;
  source?: string;
  source_label?: string | null;
}

export interface BudgetVerification {
  valid: boolean;
  message?: string;
  project_id?: string;
  project_name?: string | null;
  company_name?: string | null;
  budget_number: string;
  title: string;
  status: string;
  total_amount: string;
  currency: string;
  verification_hash: string;
  items_count: number;
  approved_at: string | null;
  created_at: string;
  generated_at?: string;
  items: BudgetVerificationItem[];
}

export interface ReportVerification {
  valid: boolean;
  message?: string;
  id: string;
  project_id: string;
  report_type: string;
  report_type_label: string;
  language: string;
  currency: string;
  title: string;
  verification_hash: string;
  file_size_bytes: number | null;
  qr_code_data: string | null;
  created_at: string;
}
