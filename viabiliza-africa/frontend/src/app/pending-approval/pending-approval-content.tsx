"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Clock3, Mail, Radio, ShieldCheck } from "lucide-react";

import { useI18n } from "@/components/providers/locale-provider";
import { useApprovalStatusPoll } from "@/features/auth/hooks/use-approval-status-poll";

export default function PendingApprovalContent() {
  const { t } = useI18n();
  const searchParams = useSearchParams();
  const email = searchParams.get("email");

  useApprovalStatusPoll(email);

  return (
    <div className="mx-auto flex max-w-lg flex-col items-center py-4 text-center">
      <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-teal-50 text-teal-700 ring-1 ring-teal-100">
        <ShieldCheck className="h-8 w-8" />
      </div>
      <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-teal-700">
        {t("auth.pendingBadge")}
      </p>
      <h1 className="mt-2 text-2xl font-bold tracking-tight text-zinc-900">{t("auth.pendingTitle")}</h1>
      <p className="mt-3 text-sm leading-relaxed text-zinc-600">{t("auth.pendingBody")}</p>

      {email ? (
        <>
          <p className="mt-4 inline-flex items-center gap-2 rounded-full bg-zinc-100 px-3 py-1.5 text-sm font-medium text-zinc-700">
            <Mail className="h-4 w-4" />
            {email}
          </p>
          <p className="mt-3 inline-flex items-center gap-2 text-xs font-medium text-teal-700">
            <Radio className="h-3.5 w-3.5 animate-pulse" />
            {t("auth.pendingPolling")}
          </p>
        </>
      ) : null}

      <div className="mt-8 w-full rounded-2xl border border-zinc-200 bg-white p-4 text-left shadow-sm">
        <div className="flex items-start gap-3">
          <Clock3 className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
          <div>
            <p className="text-sm font-semibold text-zinc-900">{t("auth.pendingNextTitle")}</p>
            <p className="mt-1 text-sm text-zinc-600">{t("auth.pendingNextBody")}</p>
          </div>
        </div>
      </div>

      <p className="mt-6 max-w-sm text-xs text-zinc-500">{t("auth.pendingRealtimeHint")}</p>

      <Link href="/login" className="mt-6 text-sm font-semibold text-teal-700 hover:underline">
        ← {t("auth.backToLogin")}
      </Link>
    </div>
  );
}
