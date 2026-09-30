import { apiRequest } from "@/lib/api/http-client";

import type { AuthResponse, RegistrationConfig, User, UserRole } from "@/lib/types/auth";

type GoogleConfig = { enabled: boolean; client_id: string | null };

let googleConfigRequest: Promise<GoogleConfig> | null = null;

export const authApi = {
  registrationConfig() {
    return apiRequest<RegistrationConfig>("/auth/registration/config", "GET", undefined, false);
  },

  registrationStatus(email: string) {
    const query = encodeURIComponent(email.trim().toLowerCase());
    return apiRequest<{
      status: "active" | "pending_approval" | "unknown";
      can_sign_in: boolean;
      role?: string;
    }>(`/auth/registration/status?email=${query}`, "GET", undefined, false);
  },

  googleConfig() {
    if (!googleConfigRequest) {
      googleConfigRequest = apiRequest<GoogleConfig>(
        "/auth/google/config",
        "GET",
        undefined,
        false,
      ).catch((err) => {
        googleConfigRequest = null;
        throw err;
      });
    }
    return googleConfigRequest;
  },

  googleAuth(payload: {
    code?: string;
    credential?: string;
    terms_accepted?: boolean;
    terms_version?: string;
  }) {
    return apiRequest<AuthResponse & { is_new_user?: boolean }>(
      "/auth/google",
      "POST",
      payload,
      false,
    );
  },

  login(email: string, password: string) {
    return apiRequest<AuthResponse>("/auth/login", "POST", { email, password }, false);
  },

  register(payload: {
    email: string;
    password: string;
    full_name: string;
    role: Exclude<UserRole, "admin">;
    bank_code?: string;
  }) {
    return apiRequest<User>("/auth/register", "POST", payload);
  },

  me() {
    return apiRequest<User>("/auth/me", "GET");
  },

  updatePreferences(payload: { preferred_currency: "AOA" | "USD" | "EUR" }) {
    return apiRequest<User>("/auth/me/preferences", "PATCH", payload);
  },

  logout(refreshToken?: string | null) {
    return apiRequest<{ message: string }>("/auth/logout", "POST", {
      refresh_token: refreshToken ?? null,
    });
  },

  refresh(refreshToken: string) {
    return apiRequest<Pick<AuthResponse, "access_token" | "refresh_token" | "expires_in">>(
      "/auth/refresh",
      "POST",
      { refresh_token: refreshToken },
      false,
    );
  },

  recoverPassword(email: string) {
    return apiRequest<{ message: string }>("/auth/recover-password", "POST", { email }, false);
  },

  requestSignupOtp(payload: {
    email: string;
    password: string;
    full_name: string;
    terms_accepted: boolean;
    terms_version?: string;
  }) {
    return apiRequest<{ message: string; expires_in_minutes: number; dev_otp?: string }>(
      "/auth/signup/request-otp",
      "POST",
      payload,
      false,
    );
  },

  verifySignupOtp(email: string, code: string, terms: { terms_accepted: boolean; terms_version?: string }) {
    return apiRequest<AuthResponse>("/auth/signup/verify-otp", "POST", { email, code, ...terms }, false);
  },

  resendSignupOtp(email: string) {
    return apiRequest<{ message: string; dev_otp?: string }>(
      "/auth/signup/resend-otp",
      "POST",
      { email },
      false,
    );
  },

  resetPassword(token: string, newPassword: string) {
    return apiRequest<{ message: string }>(
      "/auth/reset-password",
      "POST",
      { token, new_password: newPassword },
      false,
    );
  },
};
