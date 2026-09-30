"use client";

import { useMemo, useState } from "react";
import { TrendingDown, TrendingUp } from "lucide-react";

import { useI18n } from "@/components/providers/locale-provider";
import { AnimatedAreaChart, AnimatedBarChart } from "@/features/dashboard/components/animated-charts";
import { AnimatedDonutChart } from "@/features/dashboard/components/animated-donut-chart";
import { type DashboardMetrics } from "@/features/dashboard/lib/dashboard-analytics";
import { useAnimatedNumber } from "@/hooks/use-animated-number";
import { useInView } from "@/hooks/use-in-view";

type ChartView = "area" | "bars" | "sectors";

function GrowthBadge({ pct, label }: { pct: number | null; label: string }) {
  if (pct == null) return null;
  const positive = pct >= 0;
  const Icon = positive ? TrendingUp : TrendingDown;

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold va-badge-pop ${
        positive ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"
      }`}
    >
      <Icon className="h-3 w-3" />
      {label}
    </span>
  );
}

export function DashboardInvestmentChart({ metrics, enterDelay = 0 }: { metrics: DashboardMetrics; enterDelay?: number }) {
  const { t, intlLocale, formatCompactMoney } = useI18n();
  const { ref, inView } = useInView();
  const [view, setView] = useState<ChartView>("area");
  const [mode, setMode] = useState<"investment" | "projects">("investment");

  const totalInvestment = metrics.monthlyTrend.reduce((s, m) => s + m.investment, 0);
  const totalProjects = metrics.monthlyTrend.reduce((s, m) => s + m.projects, 0);
  const animatedInvestment = useAnimatedNumber(totalInvestment, 1400, inView);
  const animatedProjects = useAnimatedNumber(totalProjects, 1200, inView);

  const headline = useMemo(() => {
    if (mode === "investment") return formatCompactMoney(animatedInvestment);
    return String(Math.round(animatedProjects));
  }, [mode, animatedInvestment, animatedProjects, formatCompactMoney]);

  const growthPct = mode === "investment" ? metrics.investmentGrowthPct : metrics.projectsGrowthPct;
  const growthLabel =
    growthPct != null
      ? growthPct >= 0
        ? t("dashboard.chart.growthUp", { pct: growthPct })
        : t("dashboard.chart.growthDown", { pct: Math.abs(growthPct) })
      : "";

  const views: { key: ChartView; label: string }[] = [
    { key: "area", label: t("dashboard.chart.modeArea") },
    { key: "bars", label: t("dashboard.chart.modeBars") },
    { key: "sectors", label: t("dashboard.chart.modeSectors") },
  ];

  return (
    <section ref={ref} className="va-glass-card va-dash-enter overflow-hidden p-4" style={{ animationDelay: `${enterDelay}ms` }}>
      <div className="mb-3 flex flex-wrap items-start justify-between gap-2">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <p className="text-[10px] font-semibold uppercase tracking-wider text-[var(--muted-subtle)]">
              {t("dashboard.chart.eyebrow")}
            </p>
            <span className="inline-flex items-center gap-1 text-[10px] font-medium text-emerald-600">
              <span className="va-live-dot h-1.5 w-1.5 rounded-full bg-emerald-500" />
              {t("dashboard.hero.live")}
            </span>
          </div>
          <div className="mt-0.5 flex flex-wrap items-center gap-2">
            <h2 className="text-2xl font-bold tabular-nums text-[var(--foreground)] va-count-glow">{headline}</h2>
            <GrowthBadge pct={growthPct} label={growthLabel} />
          </div>
          <p className="text-xs text-[var(--muted)]">{t("dashboard.chart.subtitle")}</p>
        </div>

        {view !== "sectors" ? (
          <div className="inline-flex rounded-md border border-[var(--border)] bg-slate-50 p-0.5 text-xs font-medium">
            {(["investment", "projects"] as const).map((key) => (
              <button
                key={key}
                type="button"
                onClick={() => setMode(key)}
                className={`rounded px-3 py-1 transition-all duration-200 ${
                  mode === key
                    ? "va-nav-pill-active shadow-sm"
                    : "text-[var(--muted)] hover:text-[var(--foreground)]"
                }`}
              >
                {key === "investment"
                  ? t("dashboard.chart.modeInvestment")
                  : t("dashboard.chart.modeProjects")}
              </button>
            ))}
          </div>
        ) : null}
      </div>

      <div className="mb-3 inline-flex rounded-md border border-[var(--border)] bg-white p-0.5 text-xs font-medium">
        {views.map((item) => (
          <button
            key={item.key}
            type="button"
            onClick={() => setView(item.key)}
            className={`rounded px-3 py-1 transition-all duration-200 ${
              view === item.key
                ? "bg-[var(--accent-soft)] font-semibold text-[#115e59]"
                : "text-[var(--muted)] hover:text-[var(--foreground)]"
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>

      <div key={`${view}-${mode}`} className="va-chart-switch">
        {view === "area" ? (
          <AnimatedAreaChart data={metrics.monthlyTrend} mode={mode} locale={intlLocale} currency={metrics.displayCurrency} active={inView} />
        ) : null}
        {view === "bars" ? (
          <AnimatedBarChart data={metrics.monthlyTrend} mode={mode} locale={intlLocale} currency={metrics.displayCurrency} active={inView} />
        ) : null}
        {view === "sectors" ? (
          metrics.sectorBreakdown.length > 0 ? (
            <AnimatedDonutChart sectors={metrics.sectorBreakdown} active={inView} />
          ) : (
            <p className="py-8 text-center text-sm text-[var(--muted)]">{t("dashboard.chart.noSectors")}</p>
          )
        ) : null}
      </div>
    </section>
  );
}
