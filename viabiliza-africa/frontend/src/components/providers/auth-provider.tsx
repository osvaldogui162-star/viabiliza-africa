"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { authApi } from "@/lib/api/auth-api";
import { ApiError } from "@/lib/api/http-client";
import { tokenStore } from "@/lib/auth/token-store";
import {
  clearCachedUserProfile,
  readCachedUserProfile,
  writeCachedUserProfile,
} from "@/lib/auth/user-profile-cache";
import { markAccountWelcomePending, isAccountWelcomePending } from "@/lib/auth/welcome-session";
import type { User, UserRole } from "@/lib/types/auth";

function sessionStubUser(): User | null {
  const role = tokenStore.getRole();
  if (!role) return null;
  return {
    id: "session",
    email: "",
    full_name: "",
    role: role as UserRole,
    is_active: true,
    created_at: "",
    updated_at: "",
  };
}

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string, redirectTo?: string) => Promise<void>;
  requestSignupOtp: (payload: {
    email: string;
    password: string;
    full_name: string;
    terms_accepted: boolean;
    terms_version?: string;
  }) => Promise<{ message: string; expires_in_minutes: number; dev_otp?: string }>;
  verifySignupOtp: (
    email: string,
    code: string,
    redirectTo?: string,
    terms?: { terms_accepted: boolean; terms_version?: string },
  ) => Promise<void>;
  resendSignupOtp: (email: string) => Promise<{ message: string; dev_otp?: string }>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
  loginWithGoogle: (
    code: string,
    redirectTo?: string,
    terms?: { terms_accepted: boolean; terms_version?: string },
  ) => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function postLoginPath(role: string, redirectTo?: string, welcomePending?: boolean): string {
  if (redirectTo) return redirectTo;
  if (welcomePending) return "/dashboard?welcome=1";
  if (role === "bank") return "/financiador";
  return "/dashboard";
}

function handlePendingApproval(router: ReturnType<typeof useRouter>, error: ApiError) {
  const email = error.email ?? "";
  markAccountWelcomePending();
  toast.message(error.message);
  router.push(email ? `/pending-approval?email=${encodeURIComponent(email)}` : "/pending-approval");
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [hasSession, setHasSession] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  const refreshProfile = useCallback(async () => {
    try {
      const me = await authApi.me();
      setUser(me);
      writeCachedUserProfile(me);
      const token = tokenStore.getAccessToken();
      const refresh = tokenStore.getRefreshToken();
      if (token && refresh) {
        tokenStore.setSession(token, refresh, me.role);
      }
      setHasSession(true);
    } catch {
      tokenStore.clear();
      clearCachedUserProfile();
      setUser(null);
      setHasSession(false);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const token = tokenStore.getAccessToken();
    if (!token) {
      setHasSession(false);
      setIsLoading(false);
      return;
    }

    setHasSession(true);
    const cached = readCachedUserProfile();
    if (cached) {
      setUser(cached);
      setIsLoading(false);
      void refreshProfile();
      return;
    }

    const stub = sessionStubUser();
    if (stub) {
      setUser(stub);
      setIsLoading(false);
    }
    void refreshProfile();
  }, [refreshProfile]);

  const login = useCallback(
    async (email: string, password: string, redirectTo?: string) => {
      const response = await authApi.login(email, password);
      tokenStore.setSession(
        response.access_token,
        response.refresh_token,
        response.user.role,
      );
      setUser(response.user);
      writeCachedUserProfile(response.user);
      setHasSession(true);
      setIsLoading(false);
      toast.success(`Bem-vindo, ${response.user.full_name}`);
      const welcomePending = isAccountWelcomePending();
      router.push(postLoginPath(response.user.role, redirectTo, welcomePending));
    },
    [router],
  );

  const requestSignupOtp = useCallback(
    (payload: {
      email: string;
      password: string;
      full_name: string;
      terms_accepted: boolean;
      terms_version?: string;
    }) => authApi.requestSignupOtp(payload),
    [],
  );

  const verifySignupOtp = useCallback(
    async (
      email: string,
      code: string,
      redirectTo?: string,
      terms?: { terms_accepted: boolean; terms_version?: string },
    ) => {
      try {
        const response = await authApi.verifySignupOtp(email, code, {
          terms_accepted: terms?.terms_accepted ?? true,
          terms_version: terms?.terms_version,
        });
        tokenStore.setSession(
          response.access_token,
          response.refresh_token,
          response.user.role,
        );
        setUser(response.user);
        writeCachedUserProfile(response.user);
        setHasSession(true);
        setIsLoading(false);
        markAccountWelcomePending();
        router.push(redirectTo || "/dashboard?welcome=1");
      } catch (error) {
        if (error instanceof ApiError && error.code === "account_pending_approval") {
          handlePendingApproval(router, error);
          return;
        }
        throw error;
      }
    },
    [router],
  );

  const resendSignupOtp = useCallback(
    (email: string) => authApi.resendSignupOtp(email),
    [],
  );

  const loginWithGoogle = useCallback(
    async (
      code: string,
      redirectTo?: string,
      terms?: { terms_accepted: boolean; terms_version?: string },
    ) => {
      try {
        const response = await authApi.googleAuth({
          code,
          terms_accepted: terms?.terms_accepted ?? false,
          terms_version: terms?.terms_version,
        });
        tokenStore.setSession(
          response.access_token,
          response.refresh_token,
          response.user.role,
        );
        setUser(response.user);
        writeCachedUserProfile(response.user);
        setHasSession(true);
        setIsLoading(false);
        toast.success(`Bem-vindo, ${response.user.full_name}`);
        const welcomePending = isAccountWelcomePending();
        if (response.is_new_user) {
          markAccountWelcomePending();
        }
        const showWelcome = response.is_new_user || welcomePending;
        router.push(
          postLoginPath(response.user.role, redirectTo, showWelcome ? true : undefined),
        );
      } catch (error) {
        if (error instanceof ApiError && error.code === "account_pending_approval") {
          handlePendingApproval(router, error);
          return;
        }
        throw error;
      }
    },
    [router],
  );

  const logout = useCallback(async () => {
    try {
      await authApi.logout(tokenStore.getRefreshToken());
    } catch {
      // logout local mesmo se backend falhar
    }
    tokenStore.clear();
    clearCachedUserProfile();
    setUser(null);
    setHasSession(false);
    toast.success("Sessão terminada");
    router.push("/login");
  }, [router]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isLoading,
      isAuthenticated: !!user || hasSession,
      login,
      requestSignupOtp,
      verifySignupOtp,
      resendSignupOtp,
      logout,
      refreshProfile,
      loginWithGoogle,
    }),
    [user, isLoading, hasSession, login, requestSignupOtp, verifySignupOtp, resendSignupOtp, logout, refreshProfile, loginWithGoogle],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth deve ser usado dentro de AuthProvider");
  }
  return context;
}
