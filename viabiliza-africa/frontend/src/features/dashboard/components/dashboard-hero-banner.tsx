"use client";

import Link from "next/link";
import { ArrowUpRight, Plus, Sparkles } from "lucide-react";

import { DashboardActionButton } from "@/features/dashboard/components/dashboard-action-button";
import { useI18n } from "@/components/providers/locale-provider";

type DashboardHeroBannerProps = {
  userName: string;
  isWelcome?: boolean;
  canCreate: boolean;
  planName: string;
  projectsTotal: number;
  delay?: number;
};

export function DashboardHeroBanner({
  userName,
  isWelcome,
  canCreate,
  planName,
  projectsTotal,
  delay = 0,
}: DashboardHeroBannerProps) {
  const { t } = useI18n();
  const firstName = userName.trim().split(/\s+/)[0] || userName;

  return (
    <header
      className="va-glass-card va-dash-enter va-hero-glow relative overflow-hidden p-4"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="pointer-events-none absolute -right-16 -top-16 h-48 w-48 rounded-full bg-teal-400/10 blur-3xl va-hero-orb" />
      <div className="pointer-events-none absolute -bottom-12 left-1/3 h-32 w-32 rounded-full bg-emerald-400/8 blur-2xl va-hero-orb-delayed" />

      <div className="relative flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0 space-y-1.5">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1.5 rounded-md bg-[var(--accent-soft)] px-2 py-0.5 text-[11px] font-semibold text-[#115e59]">
              <Sparkles className="h-3 w-3 text-[var(--primary)]" />
              {isWelcome ? t("dashboard.hero.welcomeBadge") : t("dashboard.hero.badge")}
            </span>
            <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-600">
              <span className="va-live-dot h-1.5 w-1.5 rounded-full bg-emerald-500" />
              {t("dashboard.hero.live")}
            </span>
            <span className="text-[11px] font-medium text-[var(--muted)]">{planName}</span>
          </div>
          <h1 className="text-xl font-bold tracking-tight text-[var(--foreground)] sm:text-2xl">
            {t("dashboard.hero.greeting", { name: firstName })}
          </h1>
          <p className="max-w-xl text-sm text-[var(--muted)]">
            {canCreate ? t("dashboard.hero.subtitleAnalyst") : t("dashboard.hero.subtitleCollaborator")}
          </p>
          <p className="text-[11px] text-[var(--muted-subtle)]">
            {t("dashboard.recentHint", { total: projectsTotal })}
          </p>
        </div>

        <div className="flex shrink-0 flex-wrap gap-2">
          {canCreate ? (
            <DashboardActionButton href="/projects/new" variant="primary" className="inline-flex items-center gap-1.5">
              <Plus className="h-3.5 w-3.5" />
              {t("dashboard.new")}
            </DashboardActionButton>
          ) : null}
          <DashboardActionButton href="/planos" variant="secondary" className="inline-flex items-center gap-1.5">
            {t("dashboard.hero.explorePlans")}
            <ArrowUpRight className="h-3.5 w-3.5 text-[var(--muted-subtle)]" />
          </DashboardActionButton>
        </div>
      </div>
    </header>
  );
}
