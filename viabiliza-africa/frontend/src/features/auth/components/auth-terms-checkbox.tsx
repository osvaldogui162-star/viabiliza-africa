"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { useI18n } from "@/components/providers/locale-provider";
import { authApi } from "@/lib/api/auth-api";
import { cn } from "@/lib/utils/cn";

export function useRegistrationConfig() {
  const [config, setConfig] = useState<{
    mode: string;
    terms_version: string;
    require_terms: boolean;
  } | null>(null);

  useEffect(() => {
    let cancelled = false;
    void authApi
      .registrationConfig()
      .then((data) => {
        if (!cancelled) setConfig(data);
      })
      .catch(() => {
        if (!cancelled) {
          setConfig({ mode: "admin_approval", terms_version: "2026-01", require_terms: true });
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return config;
}

export function AuthTermsCheckbox({
  checked,
  onChange,
  className,
}: {
  checked: boolean;
  onChange: (value: boolean) => void;
  className?: string;
}) {
  const { t } = useI18n();

  return (
    <label
      className={cn(
        "flex cursor-pointer items-start gap-2.5 rounded-xl border border-zinc-200/90 bg-zinc-50/80 px-3.5 py-3 text-sm leading-snug text-zinc-600",
        className,
      )}
    >
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="mt-0.5 h-4 w-4 shrink-0 rounded border-zinc-300 text-teal-600 focus:ring-teal-500"
      />
      <span>
        {t("auth.termsPrefix")}{" "}
        <Link href="/termos" className="font-semibold text-teal-700 hover:underline" target="_blank">
          {t("auth.termsLink")}
        </Link>{" "}
        {t("auth.termsAnd")}{" "}
        <Link href="/privacidade" className="font-semibold text-teal-700 hover:underline" target="_blank">
          {t("auth.privacyLink")}
        </Link>
        .
      </span>
    </label>
  );
}
