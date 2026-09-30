"use client";

import { Crown, Sparkles } from "lucide-react";

import { DashboardActionButton } from "@/features/dashboard/components/dashboard-action-button";
import { useI18n } from "@/components/providers/locale-provider";
import { useAnimatedNumber } from "@/hooks/use-animated-number";
import { useInView } from "@/hooks/use-in-view";
import type { MySubscriptionResponse } from "@/lib/types/subscription";

type DashboardPlanWidgetProps = {
  subscription: MySubscriptionResponse | null;
  metricsPlanPct: number | null;
};

function Meter({
  label,
  used,
  limit,
  active,
  delay,
}: {
  label: string;
  used: number;
  limit: number | null;
  active: boolean;
  delay: number;
}) {
  const pct = limit != null && limit > 0 ? Math.min(100, Math.round((used / limit) * 100)) : 8;
  const animPct = useAnimatedNumber(pct, 900, active);

  return (
    <div style={{ animationDelay: `${delay}ms` }}>
      <div className="mb-1 flex items-center justify-between text-[11px]">
        <span className="font-medium text-[var(--foreground)]">{label}</span>
        <span className="tabular-nums text-[var(--muted)]">
          {used}
          {limit != null ? ` / ${limit}` : ""}
        </span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-slate-100">
        <div
          className="va-bar-gradient h-full rounded-full transition-[width] duration-700 ease-out"
          style={{ width: `${animPct}%` }}
        />
      </div>
    </div>
  );
}

function CircularGauge({ pct, active }: { pct: number; active: boolean }) {
  const anim = useAnimatedNumber(pct, 1200, active);
  const r = 36;
  const c = 2 * Math.PI * r;
  const offset = c - (anim / 100) * c;

  return (
    <svg viewBox="0 0 88 88" className="h-[72px] w-[72px] -rotate-90" aria-hidden>
      <circle cx="44" cy="44" r={r} fill="none" stroke="#e2e8f0" strokeWidth="8" />
      <circle
        cx="44"
        cy="44"
        r={r}
        fill="none"
        stroke="url(#planGauge)"
        strokeWidth="8"
        strokeLinecap="round"
        strokeDasharray={c}
        strokeDashoffset={offset}
        className="transition-[stroke-dashoffset] duration-300 ease-out"
      />
      <defs>
        <linearGradient id="planGauge" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#0d9488" />
          <stop offset="100%" stopColor="#10b981" />
        </linearGradient>
      </defs>
    </svg>
  );
}

export function DashboardPlanWidget({
  subscription,
  metricsPlanPct,
  enterDelay = 0,
}: DashboardPlanWidgetProps & { enterDelay?: number }) {
  const { t } = useI18n();
  const { ref, inView } = useInView();

  if (!subscription) {
    return (
      <section className="va-glass-card p-4">
        <p className="text-sm text-[var(--muted)]">{t("dashboard.plan.loading")}</p>
      </section>
    );
  }

  const { plan, usage, capabilities } = subscription;
  const projectsLimit = usage.projects_limit ?? capabilities.projects_limit;
  const teamLimit = usage.team_members_limit ?? capabilities.team_members_limit;
  const animPct = useAnimatedNumber(metricsPlanPct ?? 0, 1200, inView);

  return (
    <section ref={ref} className="va-glass-card va-dash-enter p-4" style={{ animationDelay: `${enterDelay}ms` }}>
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-wider text-[var(--muted-subtle)]">
            {t("nav.subscription")}
          </p>
          <h3 className="mt-0.5 flex items-center gap-1.5 text-base font-bold text-[var(--foreground)]">
            {plan.name}
            <Crown className="h-3.5 w-3.5 text-amber-500" />
          </h3>
          <p className="text-[11px] text-[var(--muted)]">
            {capabilities.support_sla ?? t("dashboard.plan.defaultSla")}
          </p>
        </div>
        {metricsPlanPct != null ? (
          <div className="relative flex items-center justify-center">
            <CircularGauge pct={metricsPlanPct} active={inView} />
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <p className="text-sm font-bold tabular-nums text-[var(--primary)]">{Math.round(animPct)}%</p>
            </div>
          </div>
        ) : null}
      </div>

      <div className="mt-3 space-y-2.5">
        <Meter
          label={t("dashboard.plan.projects")}
          used={usage.projects_count}
          limit={projectsLimit}
          active={inView}
          delay={0}
        />
        <Meter
          label={t("dashboard.plan.team")}
          used={1 + usage.collaborators_count}
          limit={teamLimit}
          active={inView}
          delay={100}
        />
        {usage.scraping_items_limit != null && usage.scraping_items_limit > 0 ? (
          <Meter
            label={t("dashboard.plan.scraping")}
            used={usage.scraping_items_this_month}
            limit={usage.scraping_items_limit}
            active={inView}
            delay={200}
          />
        ) : null}
      </div>

      {(capabilities.monte_carlo_enabled || capabilities.reports_bfa || capabilities.scraping_enabled) && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {capabilities.monte_carlo_enabled ? (
            <span className="rounded-md bg-[var(--accent-soft)] px-2 py-0.5 text-[10px] font-semibold text-[#115e59]">
              Monte Carlo
            </span>
          ) : null}
          {capabilities.reports_bfa ? (
            <span className="rounded-md bg-[var(--accent-soft)] px-2 py-0.5 text-[10px] font-semibold text-[#115e59]">
              BFA · BDA
            </span>
          ) : null}
          {capabilities.scraping_enabled ? (
            <span className="rounded-md bg-[var(--accent-soft)] px-2 py-0.5 text-[10px] font-semibold text-[#115e59]">
              Scraping
            </span>
          ) : null}
        </div>
      )}

      <DashboardActionButton
        href="/conta/assinatura"
        variant="primary"
        className="mt-3 flex w-full items-center justify-center gap-1.5 py-2"
      >
        <Sparkles className="h-3.5 w-3.5" />
        {t("dashboard.plan.manage")}
      </DashboardActionButton>
    </section>
  );
}
