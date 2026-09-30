const ACCESS_KEY = "va_access_token";
const REFRESH_KEY = "va_refresh_token";
const USER_ROLE_KEY = "va_user_role";

export const tokenStore = {
  getAccessToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(ACCESS_KEY);
  },
  getRefreshToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(REFRESH_KEY);
  },
  getRole(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(USER_ROLE_KEY);
  },
  setSession(accessToken: string, refreshToken: string, role: string) {
    if (typeof window === "undefined") return;
    localStorage.setItem(ACCESS_KEY, accessToken);
    localStorage.setItem(REFRESH_KEY, refreshToken);
    localStorage.setItem(USER_ROLE_KEY, role);
    document.cookie = `va_access_token=${encodeURIComponent(accessToken)}; path=/; max-age=604800; samesite=lax`;
    document.cookie = `va_user_role=${encodeURIComponent(role)}; path=/; max-age=604800; samesite=lax`;
  },
  clear() {
    if (typeof window === "undefined") return;
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_ROLE_KEY);
    document.cookie = "va_access_token=; path=/; max-age=0; samesite=lax";
    document.cookie = "va_user_role=; path=/; max-age=0; samesite=lax";
  },
};
