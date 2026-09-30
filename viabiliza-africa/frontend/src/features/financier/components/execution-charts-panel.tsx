"use client";

import { useI18n } from "@/components/providers/locale-provider";
import {
  BarChart,
  ChartCard,
  DonutChart,
  RadialGauge,
  TrendChart,
} from "@/features/financier/components/financier-charts";
import { useInView } from "@/hooks/use-in-view";
import type { FinancierMonitoringResponse } from "@/lib/types/financier";

export function ExecutionChartsPanel({
  data,
  theme = "light",
}: {
  data: FinancierMonitoringResponse;
  theme?: "light" | "dark";
}) {
  const { t, formatMoney } = useI18n();
  const { ref, inView } = useInView();
  const charts = data.charts;
  if (!charts) {
    return null;
  }
  const currency = charts.summary.currency;

  const fmt = (n: number) => formatMoney(n, currency);

  const legend = charts.donut_execution.filter((s) => s.value > 0);

  return (
    <section ref={ref} className="space-y-6" aria-label={t("financier.chartsTitle")}>
      <div className="grid gap-4 lg:grid-cols-3">
        <ChartCard title={t("financier.chartGauge")} theme={theme} delayMs={0}>
          <RadialGauge
            value={charts.gauge.value}
            max={charts.gauge.max}
            label={t("financier.creditUse")}
            theme={theme}
            active={inView}
          />
        </ChartCard>

        <ChartCard title={t("financier.chartBars")} theme={theme} className="lg:col-span-2" delayMs={80}>
          <BarChart bars={charts.bar_comparison} theme={theme} active={inView} />
        </ChartCard>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <ChartCard title={t("financier.chartDonut")} theme={theme} delayMs={120}>
          <DonutChart slices={charts.donut_execution} active={inView} theme={theme} />
          <ul className="mt-2 space-y-1">
            {legend.map((s) => (
              <li key={s.label} className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ background: s.color }} />
                  {s.label}
                </span>
                <span
                  className={
                    theme === "dark"
                      ? "font-semibold tabular-nums text-white"
                      : "font-semibold tabular-nums text-zinc-800"
                  }
                >
                  {fmt(s.value)}
                </span>
              </li>
            ))}
          </ul>
        </ChartCard>

        <ChartCard title={t("financier.chartTrend")} theme={theme} delayMs={160}>
          <TrendChart points={charts.spend_trend} formatMoney={fmt} theme={theme} />
        </ChartCard>
      </div>
    </section>
  );
}
