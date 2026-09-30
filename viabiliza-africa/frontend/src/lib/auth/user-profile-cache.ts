import type { User } from "@/lib/types/auth";

const CACHE_KEY = "va_user_profile";

export function readCachedUserProfile(): User | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(CACHE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

export function writeCachedUserProfile(user: User): void {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.setItem(CACHE_KEY, JSON.stringify(user));
  } catch {
    /* quota / private mode */
  }
}

export function clearCachedUserProfile(): void {
  if (typeof window === "undefined") return;
  sessionStorage.removeItem(CACHE_KEY);
}
