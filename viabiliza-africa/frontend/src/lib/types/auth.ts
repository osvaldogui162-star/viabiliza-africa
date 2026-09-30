export type UserRole = "admin" | "financial" | "user" | "bank";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  preferred_currency?: "AOA" | "USD" | "EUR";
  bank_code?: string | null;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface ApiErrorShape {
  error?: {
    code?: string;
    message?: string;
    email?: string;
    details?: Record<string, string[]>;
  };
}

export interface RegistrationConfig {
  mode: "open" | "invite_only" | "admin_approval";
  terms_version: string;
  require_terms: boolean;
}
