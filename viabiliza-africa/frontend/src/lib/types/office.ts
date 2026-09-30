export interface OfficeCapability {
  key: string;
  label_pt: string;
}

export interface OfficeProjectRow {
  id: string;
  name: string;
  company_name: string;
  status: string;
  shares_count: number;
}

export interface OfficeDashboard {
  owner: { id: string; full_name: string; email: string };
  stats: { projects_count: number; members_count: number; shared_slots: number };
  capability_catalog: OfficeCapability[];
  projects: OfficeProjectRow[];
}

export interface OfficeMember {
  id: string;
  owner_id: string;
  user_id: string | null;
  email: string;
  full_name: string;
  job_title: string;
  status: string;
  notes: string | null;
  project_ids: string[];
  created_at: string;
  updated_at: string;
}

export interface AdminOfficeSummary {
  owner_id: string;
  owner_name: string;
  owner_email: string;
  active_members: number;
  projects_count: number;
}
