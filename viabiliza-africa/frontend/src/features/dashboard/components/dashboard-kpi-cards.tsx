"use client";

import { FolderKanban, Layers, Share2, TrendingDown, TrendingUp, Wallet } from "lucide-react";

import { useI18n } from "@/components/providers/locale-provider";
import { Sparkline } from "@/features/dashboard/components/sparkline";
import { type DashboardMetrics } from "@/features/dashboard/lib/dashboard-analytics";
import { useAnimatedNumber } from "@/hooks/use-animated-number";
import { useInView } from "@/hooks/use-in-view";

type DashboardKpiCardsProps = {
  metrics: DashboardMetrics;
  baseDelay?: number;
};

function TrendChip({ value }: { value: number | null }) {
  if (value == null || value === 0) return null;
  const up = value > 0;
  const Icon = up ? TrendingUp : TrendingDown;
  return (
    <span
      className={`va-badge-pop inline-flex items-center gap-0.5 rounded px-1.5 py-0.5 text-[10px] font-semibold ${
        up ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"
      }`}
    >
      <Icon className="h-2.5 w-2.5" />
      {up ? "+" : ""}
      {value}%
    </span>
  );
}

export function DashboardKpiCards({ metrics, baseDelay = 80 }: DashboardKpiCardsProps) {
  const { t, formatCompactMoney } = useI18n();
  const { ref, inView } = useInView();

  const animProjects = useAnimatedNumber(metrics.totalProjects, 1000, inView);
  const animInvestment = useAnimatedNumber(metrics.totalInvestment, 1400, inView);
  const animBudgets = useAnimatedNumber(metrics.approvedBudgets, 900, inView);
  const animShared = useAnimatedNumber(metrics.sharedProjects, 800, inView);

  const projectSpark = metrics.monthlyTrend.map((m) => m.projects);
  const investSpark = metrics.monthlyTrend.map((m) => m.investment);

  const cards = [
    {
      label: t("dashboard.totalProjects"),
      display: String(Math.round(animProjects)),
      sub: t("dashboard.kpi.projectsSub", { active: metrics.activeProjects }),
      icon: FolderKanban,
      spark: projectSpark,
      trend: metrics.projectsGrowthPct,
      delay: baseDelay,
    },
    {
      label: t("dashboard.kpi.investmentTotal"),
      display: formatCompactMoney(animInvestment),
      sub: t("dashboard.kpi.investmentSub", { currency: metrics.displayCurrency }),
      icon: Wallet,
      spark: investSpark,
      trend: metrics.investmentGrowthPct,
      delay: baseDelay + 70,
    },
    {
      label: t("dashboard.kpi.approvedBudgets"),
      display: String(Math.round(animBudgets)),
      sub: t("dashboard.kpi.budgetsSub", { drafts: metrics.draftProjects }),
      icon: Layers,
      spark: investSpark.map((v, i) => (projectSpark[i] > 0 ? v / projectSpark[i] : 0)),
      trend: null,
      delay: baseDelay + 140,
    },
    {
      label: t("dashboard.sharedWithMe"),
      display: String(Math.round(animShared)),
      sub:
        metrics.planUsagePct != null
          ? t("dashboard.kpi.planUsage", { pct: metrics.planUsagePct })
          : t("dashboard.kpi.unlimitedPlan"),
      icon: Share2,
      spark: projectSpark,
      trend: null,
      delay: baseDelay + 210,
    },
  ];

  return (
    <div ref={ref} className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <article
            key={card.label}
            className="va-glass-card va-dash-enter group relative overflow-hidden p-4 transition-shadow duration-300 hover:shadow-md hover:shadow-teal-500/5"
            style={{ animationDelay: `${card.delay}ms` }}
          >
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-teal-50/0 to-teal-50/0 transition duration-300 group-hover:from-teal-50/40 group-hover:to-transparent" />
            <div className="relative flex items-start justify-between gap-2">
              <span className="va-icon-box h-10 w-10 shrink-0 transition duration-300 group-hover:scale-110 group-hover:shadow-sm">
                <Icon className="h-4 w-4" />
              </span>
              <TrendChip value={card.trend} />
            </div>
            <p className="relative mt-3 text-2xl font-bold leading-none tabular-nums text-[var(--foreground)] va-count-glow">
              {card.display}
            </p>
            <p className="relative mt-1.5 truncate text-xs font-semibold text-[var(--foreground)]">{card.label}</p>
            <p className="relative mt-0.5 truncate text-[11px] text-[var(--muted)]">{card.sub}</p>
            <div className="relative mt-3 flex justify-end">
              <Sparkline data={card.spark} active={inView} />
            </div>
          </article>
        );
      })}
    </div>
  );
}
