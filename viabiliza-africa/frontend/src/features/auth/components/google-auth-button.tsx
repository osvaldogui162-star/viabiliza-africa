"use client";

import { Loader2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";

import { useAuth } from "@/components/providers/auth-provider";
import { useI18n } from "@/components/providers/locale-provider";
import { authApi } from "@/lib/api/auth-api";
import { ApiError } from "@/lib/api/http-client";
import { cn } from "@/lib/utils/cn";

const ENV_GOOGLE_CLIENT_ID =
  process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID?.trim() || null;

declare global {
  interface Window {
    google?: {
      accounts: {
        oauth2: {
          initCodeClient: (config: {
            client_id: string;
            scope: string;
            ux_mode: "popup" | "redirect";
            callback: (response: { code?: string; error?: string }) => void;
          }) => { requestCode: () => void };
        };
      };
    };
  }
}

function GoogleLogo({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      aria-hidden
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
        fill="#4285F4"
      />
      <path
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
        fill="#34A853"
      />
      <path
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
        fill="#FBBC05"
      />
      <path
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
        fill="#EA4335"
      />
    </svg>
  );
}

function useGoogleClientId() {
  const [clientId, setClientId] = useState<string | null>(ENV_GOOGLE_CLIENT_ID);
  const [loading, setLoading] = useState(!ENV_GOOGLE_CLIENT_ID);

  useEffect(() => {
    let cancelled = false;
    let attempts = 0;

    const load = async () => {
      try {
        const config = await authApi.googleConfig();
        if (cancelled) return;
        if (config.enabled && config.client_id) {
          setClientId(config.client_id);
        } else if (!ENV_GOOGLE_CLIENT_ID) {
          setClientId(null);
        }
      } catch {
        if (cancelled) return;
        if (ENV_GOOGLE_CLIENT_ID) {
          setClientId(ENV_GOOGLE_CLIENT_ID);
          return;
        }
        attempts += 1;
        if (attempts < 4) {
          window.setTimeout(() => void load(), 1500 * attempts);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  return { clientId, loading, enabled: !!clientId };
}

export function GoogleAuthButton({
  redirectTo,
  compact,
  className,
  onSuccess,
  requireTerms = false,
  termsAccepted = false,
  termsVersion,
}: {
  redirectTo?: string;
  compact?: boolean;
  className?: string;
  onSuccess?: () => void;
  /** Só obrigatório no registo (signup), não no login. */
  requireTerms?: boolean;
  termsAccepted?: boolean;
  termsVersion?: string;
}) {
  const { loginWithGoogle } = useAuth();
  const { t } = useI18n();
  const { clientId, loading: configLoading } = useGoogleClientId();
  const [scriptReady, setScriptReady] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!clientId) return;

    const existing = document.querySelector('script[data-google-gsi="true"]');
    if (existing) {
      setScriptReady(true);
      return;
    }

    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    script.dataset.googleGsi = "true";
    script.onload = () => setScriptReady(true);
    script.onerror = () => toast.error(t("auth.googleUnavailable"));
    document.head.appendChild(script);
  }, [clientId, t]);

  const handleClick = useCallback(() => {
    if (requireTerms && !termsAccepted) {
      toast.error(t("auth.termsRequired"));
      return;
    }
    if (!clientId || !scriptReady || !window.google?.accounts?.oauth2) {
      toast.error(t("auth.googleUnavailable"));
      return;
    }

    setLoading(true);
    const resetLoading = () => setLoading(false);
    const safetyTimer = window.setTimeout(resetLoading, 120_000);

    const client = window.google.accounts.oauth2.initCodeClient({
      client_id: clientId,
      scope: "openid email profile",
      ux_mode: "popup",
      callback: (response) => {
        window.clearTimeout(safetyTimer);
        void (async () => {
          try {
            if (response.error || !response.code) {
              if (response.error !== "access_denied") {
                toast.error(t("auth.googleFailed"));
              }
              return;
            }
            await loginWithGoogle(
              response.code,
              redirectTo,
              requireTerms
                ? { terms_accepted: termsAccepted ?? false, terms_version: termsVersion }
                : undefined,
            );
            onSuccess?.();
          } catch (error) {
            toast.error(error instanceof ApiError ? error.message : t("auth.googleFailed"));
          } finally {
            resetLoading();
          }
        })();
      },
    });
    client.requestCode();
  }, [clientId, scriptReady, loginWithGoogle, redirectTo, onSuccess, t, requireTerms, termsAccepted, termsVersion]);

  if (!clientId && !configLoading) return null;

  if (!clientId) {
    return (
      <div
        className={cn(
          "flex w-full items-center justify-center gap-3 rounded-xl border border-zinc-200 bg-zinc-50 font-semibold text-zinc-400",
          compact ? "min-h-[2.75rem] px-4 py-2.5 text-sm" : "min-h-[3rem] px-4 py-3 text-base",
          className,
        )}
      >
        <Loader2 className="h-5 w-5 animate-spin" />
        <span>{t("auth.continueWithGoogle")}</span>
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={loading || !scriptReady}
      className={cn(
        "group relative flex w-full items-center justify-center gap-3 rounded-xl border border-zinc-200 bg-white font-semibold text-[#1f2937] shadow-sm transition",
        "hover:border-zinc-300 hover:bg-zinc-50 hover:shadow-md",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-200 focus-visible:ring-offset-2",
        "disabled:cursor-not-allowed disabled:opacity-60",
        compact ? "min-h-[2.75rem] px-4 py-2.5 text-sm" : "min-h-[3rem] px-4 py-3 text-base sm:min-h-[3.125rem] sm:text-[1.05rem]",
        className,
      )}
    >
      {loading || !scriptReady ? (
        <Loader2 className="h-5 w-5 animate-spin text-zinc-500" />
      ) : (
        <GoogleLogo className="h-5 w-5 shrink-0 sm:h-[1.35rem] sm:w-[1.35rem]" />
      )}
      <span>{t("auth.continueWithGoogle")}</span>
    </button>
  );
}

export function AuthSocialDivider() {
  const { t } = useI18n();
  return (
    <div className="relative py-1">
      <div className="absolute inset-0 flex items-center" aria-hidden>
        <div className="w-full border-t border-zinc-200" />
      </div>
      <div className="relative flex justify-center">
        <span className="bg-white px-3 text-sm font-medium text-zinc-400">{t("auth.orContinueWith")}</span>
      </div>
    </div>
  );
}

export function AuthSocialSection({
  redirectTo,
  requireTerms = false,
  termsAccepted,
  termsVersion,
}: {
  redirectTo?: string;
  requireTerms?: boolean;
  termsAccepted?: boolean;
  termsVersion?: string;
}) {
  const { enabled, loading } = useGoogleClientId();

  if (!enabled && !loading) return null;

  return (
    <div className="space-y-4">
      <GoogleAuthButton
        redirectTo={redirectTo}
        requireTerms={requireTerms}
        termsAccepted={termsAccepted}
        termsVersion={termsVersion}
      />
      <AuthSocialDivider />
    </div>
  );
}
