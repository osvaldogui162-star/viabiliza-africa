"use client";

import Link from "next/link";
import { AlertTriangle, Info } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useI18n } from "@/components/providers/locale-provider";
import type { MySubscriptionResponse } from "@/lib/types/subscription";

type PlanLimitBannerProps = {
  subscription: MySubscriptionResponse;
};

export function PlanLimitBanner({ subscription }: PlanLimitBannerProps) {
  const { t } = useI18n();
  const { usage, plan, capabilities } = subscription;
  const limit = usage.projects_limit ?? capabilities.projects_limit;
  const used = usage.projects_count;

  if (limit == null) return null;

  const remaining = limit - used;
  const ratio = used / limit;

  if (remaining > 0 && ratio < 0.85) return null;

  const isFull = remaining <= 0;
  const Icon = isFull ? AlertTriangle : Info;

  return (
    <div
      className={`flex flex-col gap-2 rounded-lg border border-l-[3px] px-3 py-2.5 sm:flex-row sm:items-center sm:justify-between ${
        isFull
          ? "border-[var(--border)] border-l-amber-500 bg-amber-50/60"
          : "border-[var(--border)] border-l-sky-500 bg-sky-50/60"
      }`}
    >
      <div className="flex items-start gap-2">
        <Icon className={`mt-0.5 h-4 w-4 shrink-0 ${isFull ? "text-amber-600" : "text-sky-600"}`} />
        <div>
          <p className="text-xs font-semibold text-[var(--foreground)]">
            {isFull
              ? t("onboarding.projectsLimitReached", { limit: String(limit), plan: plan.name })
              : t("onboarding.projectsLimitNear", { used: String(used), limit: String(limit) })}
          </p>
          <p className="mt-0.5 text-[11px] text-[var(--muted)]">
            {isFull ? t("onboarding.projectsLimitReachedHint") : t("onboarding.projectsLimitNearHint")}
          </p>
        </div>
      </div>
      <Link href="/planos" className="shrink-0">
        <Button size="sm" variant={isFull ? "primary" : "outline"}>
          {t("onboarding.upgradePlan")}
        </Button>
      </Link>
    </div>
  );
}
