"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { useI18n } from "@/components/providers/locale-provider";
import { authApi } from "@/lib/api/auth-api";

const POLL_MS = 4000;

export function useApprovalStatusPoll(
  email: string | null | undefined,
  options?: {
    enabled?: boolean;
    redirectOnApprove?: boolean;
    onApproved?: () => void;
  },
) {
  const { t } = useI18n();
  const router = useRouter();
  const handled = useRef(false);
  const redirectOnApprove = options?.redirectOnApprove !== false;

  useEffect(() => {
    const normalized = email?.trim().toLowerCase();
    if (!normalized || options?.enabled === false) return;

    let cancelled = false;

    const check = async () => {
      if (cancelled || handled.current) return;
      try {
        const status = await authApi.registrationStatus(normalized);
        if (status.can_sign_in && status.status === "active") {
          handled.current = true;
          options?.onApproved?.();
          toast.success(t("auth.pendingApprovedLive"));
          if (redirectOnApprove) {
            router.replace(
              `/login?email=${encodeURIComponent(normalized)}&approved=1`,
            );
          }
        }
      } catch {
        // próxima tentativa
      }
    };

    void check();
    const timer = window.setInterval(() => void check(), POLL_MS);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [email, options?.enabled, options?.onApproved, redirectOnApprove, router, t]);
}
