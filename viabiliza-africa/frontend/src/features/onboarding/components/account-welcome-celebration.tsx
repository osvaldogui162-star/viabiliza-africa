"use client";

import Link from "next/link";
import { Suspense, useEffect, useMemo, useState } from "react";
import {
  ArrowRight,
  CheckCircle2,
  FolderPlus,
  MessageCircle,
  ShieldCheck,
  Sparkles,
  X,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { useAuth } from "@/components/providers/auth-provider";
import { useI18n } from "@/components/providers/locale-provider";
import { useAccountWelcome } from "@/features/onboarding/hooks/use-account-welcome";
import { cn } from "@/lib/utils/cn";

function WelcomeCelebrationInner() {
  const { user } = useAuth();
  const { t } = useI18n();
  const { visible, dismiss } = useAccountWelcome();
  const [expanded, setExpanded] = useState(true);

  const canCreate = user?.role === "admin" || user?.role === "financial";
  const firstName = user?.full_name?.trim().split(/\s+/)[0] || t("onboarding.welcomeFallback");
  const roleLabel =
    user?.role === "financial"
      ? t("onboarding.roleAnalyst")
      : user?.role === "admin"
        ? t("onboarding.roleAdmin")
        : t("onboarding.roleCollaborator");

  const tips = useMemo(
    () =>
      canCreate
        ? [t("onboarding.welcomeTipCreate"), t("onboarding.welcomeTipAnalyze")]
        : [t("onboarding.welcomeTipShared"), t("onboarding.welcomeTipChat")],
    [canCreate, t],
  );

  useEffect(() => {
    if (visible) setExpanded(true);
  }, [visible]);

  if (!user || !visible) return null;

  return (
    <div
      className="pointer-events-none fixed bottom-4 right-4 z-50 flex max-w-[min(100vw-2rem,22rem)] flex-col items-end sm:bottom-6 sm:right-6"
      role="dialog"
      aria-labelledby="va-welcome-title"
      aria-live="polite"
    >
      <div
        className={cn(
          "pointer-events-auto w-full overflow-hidden rounded-2xl border border-teal-200/70 bg-white/95 shadow-xl shadow-teal-950/10 backdrop-blur-sm transition-all duration-300",
          expanded ? "va-welcome-card--enter" : "max-h-14",
        )}
      >
        <div className="flex items-start gap-3 border-b border-teal-100/80 bg-gradient-to-r from-teal-50/90 to-white px-4 py-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-teal-600 to-emerald-600 text-white shadow-sm">
            <ShieldCheck className="h-4.5 w-4.5" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-teal-700">
              {t("onboarding.welcomeBadge")}
            </p>
            <h2 id="va-welcome-title" className="truncate text-sm font-bold text-zinc-900">
              {t("onboarding.welcomeTitle", { name: firstName })}
            </h2>
          </div>
          <div className="flex shrink-0 gap-1">
            <button
              type="button"
              onClick={() => setExpanded((v) => !v)}
              className="flex h-7 w-7 items-center justify-center rounded-lg text-zinc-400 hover:bg-zinc-100 hover:text-zinc-700"
              aria-label={expanded ? t("onboarding.minimize") : t("onboarding.expandPanel")}
            >
              <span className="text-xs font-bold">{expanded ? "−" : "+"}</span>
            </button>
            <button
              type="button"
              onClick={dismiss}
              className="flex h-7 w-7 items-center justify-center rounded-lg text-zinc-400 hover:bg-zinc-100 hover:text-zinc-700"
              aria-label={t("common.close")}
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {expanded ? (
          <div className="space-y-3 px-4 py-3">
            <p className="text-xs leading-relaxed text-zinc-600">
              {canCreate ? t("onboarding.welcomeCreatorBody") : t("onboarding.welcomeCollaboratorBody")}
            </p>

            <div className="flex flex-wrap gap-1.5">
              <span className="inline-flex items-center gap-1 rounded-full bg-teal-50 px-2 py-0.5 text-[10px] font-semibold text-teal-800 ring-1 ring-teal-100">
                <Sparkles className="h-3 w-3" />
                {t("onboarding.freePlan")}
              </span>
              <span className="inline-flex rounded-full bg-zinc-100 px-2 py-0.5 text-[10px] font-medium text-zinc-600">
                {roleLabel}
              </span>
            </div>

            <ul className="space-y-1.5">
              {tips.map((tip) => (
                <li key={tip} className="flex items-start gap-2 text-xs text-zinc-700">
                  <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-teal-600" />
                  <span>{tip}</span>
                </li>
              ))}
            </ul>

            <div className="flex flex-col gap-2 pt-1">
              {canCreate ? (
                <Link href="/projects/new" onClick={dismiss}>
                  <Button size="sm" className="h-9 w-full gap-1.5 bg-teal-600 hover:bg-teal-500">
                    <FolderPlus className="h-3.5 w-3.5" />
                    {t("onboarding.createFirstProject")}
                  </Button>
                </Link>
              ) : null}
              <Button
                size="sm"
                variant="outline"
                className="h-9 w-full gap-1.5 border-teal-200"
                onClick={dismiss}
              >
                {t("onboarding.welcomeExplore")}
                <ArrowRight className="h-3.5 w-3.5" />
              </Button>
            </div>

            <p className="flex items-center gap-1 text-[10px] text-zinc-500">
              <MessageCircle className="h-3 w-3 text-violet-500" />
              {t("onboarding.welcomeChatHint")}
            </p>
          </div>
        ) : null}
      </div>
    </div>
  );
}

export function AccountWelcomeCelebration() {
  return (
    <Suspense fallback={null}>
      <WelcomeCelebrationInner />
    </Suspense>
  );
}
