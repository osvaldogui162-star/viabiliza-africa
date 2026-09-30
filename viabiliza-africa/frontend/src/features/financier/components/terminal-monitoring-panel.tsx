"use client";

import { AlertTriangle, Link2, TrendingDown, TrendingUp } from "lucide-react";
import { useI18n } from "@/components/providers/locale-provider";
import type { TerminalMonitoringPanel } from "@/lib/types/financier";
import { cn } from "@/lib/utils/cn";

function RiskBadge({ level }: { level: string }) {
  const { t } = useI18n();
  const label =
    level === "high"
      ? t("terminal.riskHigh")
      : level === "medium"
        ? t("terminal.riskMedium")
        : t("terminal.riskLow");
  return (
    <span
      className={cn(
        "inline-flex rounded-full px-2.5 py-0.5 text-[11px] font-bold uppercase tracking-wide",
        level === "high" && "bg-rose-100 text-rose-800",
        level === "medium" && "bg-amber-100 text-amber-900",
        level === "low" && "bg-emerald-100 text-emerald-800",
      )}
    >
      {label}
    </span>
  );
}

function trendIcon(trend: string) {
  if (trend === "down") return <TrendingDown className="h-4 w-4 text-rose-600" />;
  if (trend === "up") return <TrendingUp className="h-4 w-4 text-emerald-600" />;
  return null;
}

export function TerminalMonitoringPanelView({ terminal }: { terminal: TerminalMonitoringPanel }) {
  const { t, formatMoney } = useI18n();
  const billing = terminal.billing;
  const activeAlerts = terminal.alerts ?? [];

  const formatVal = (unit: string, val: string | null | undefined) => {
    if (val == null) return "—";
    const n = parseFloat(val);
    if (unit === "money") return formatMoney(n, "AOA");
    if (unit === "pct") return `${n}%`;
    return n.toLocaleString("pt-PT");
  };

  const devLabel = (row: (typeof terminal.indicators)[0]) => {
    if (row.deviation == null) return "—";
    const suffix = row.deviation_kind === "pp" ? "pp" : "%";
    const sign = row.deviation > 0 ? "+" : "";
    return `${sign}${row.deviation}${suffix === "pp" ? " pp" : "%"}`;
  };

  return (
    <div className="space-y-5">
      <div className="bank-portal-panel rounded-2xl border border-[var(--border)] p-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-[var(--brand-teal)]">
              {t("terminal.brand")}
            </p>
            <h2 className="mt-1 font-[family-name:var(--font-poppins)] text-lg font-bold text-[var(--brand-navy)]">
              {t("terminal.previstoVsReal")}
            </h2>
            <p className="mt-1 text-sm text-[var(--muted)]">{t("terminal.previstoVsRealHint")}</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <RiskBadge level={terminal.risk_level} />
            {terminal.deviation_pct != null ? (
              <span
                className={cn(
                  "rounded-full px-3 py-1 text-sm font-bold tabular-nums",
                  terminal.deviation_pct < 0 ? "bg-rose-50 text-rose-800" : "bg-emerald-50 text-emerald-800",
                )}
              >
                {t("terminal.deviation")}: {terminal.deviation_pct > 0 ? "+" : ""}
                {terminal.deviation_pct}%
              </span>
            ) : null}
            <span
              className={cn(
                "inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold",
                billing.connected ? "bg-emerald-100 text-emerald-800" : "bg-rose-100 text-rose-900",
              )}
            >
              <Link2 className="h-3.5 w-3.5" />
              {billing.connected ? t("terminal.billingConnected") : t("terminal.billingDisconnected")}
            </span>
          </div>
        </div>

        {terminal.risk_score ? (
          <div className="mt-4 rounded-xl bg-[var(--accent-soft)] px-4 py-3">
            <p className="text-xs font-semibold uppercase text-[var(--muted)]">{t("terminal.dynamicRiskScore")}</p>
            <p className="text-2xl font-bold tabular-nums text-[var(--brand-navy)]">
              {terminal.risk_score.value}
              <span className="text-sm font-medium text-[var(--muted)]"> / 100</span>
            </p>
          </div>
        ) : null}
      </div>

      <div className="bank-portal-panel overflow-hidden rounded-2xl">
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-[#1a3a5c] text-xs uppercase tracking-wide text-white">
              <tr>
                <th className="px-4 py-3">{t("terminal.colCategory")}</th>
                <th className="px-4 py-3">{t("terminal.colIndicator")}</th>
                <th className="px-4 py-3 text-right">{t("terminal.colForecast")}</th>
                <th className="px-4 py-3 text-right">{t("terminal.colReal")}</th>
                <th className="px-4 py-3 text-center">{t("terminal.colDeviation")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border)]">
              {terminal.indicators.map((row) => (
                <tr key={row.key} className="bg-white even:bg-slate-50/80">
                  <td className="px-4 py-2.5 text-xs font-semibold uppercase text-[var(--muted)]">
                    {t(`terminal.cat_${row.category}`)}
                  </td>
                  <td className="px-4 py-2.5 font-medium text-[var(--brand-navy)]">{row.label_pt}</td>
                  <td className="px-4 py-2.5 text-right tabular-nums">{formatVal(row.unit, row.forecast)}</td>
                  <td className="px-4 py-2.5 text-right tabular-nums">{formatVal(row.unit, row.real)}</td>
                  <td
                    className={cn(
                      "px-4 py-2.5 text-center text-sm font-bold tabular-nums",
                      row.deviation != null && row.deviation < 0 && "text-rose-700",
                      row.deviation != null && row.deviation > 0 && "text-emerald-700",
                    )}
                  >
                    {devLabel(row)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="bank-portal-panel rounded-2xl p-5">
          <p className="flex items-center gap-2 text-sm font-bold text-[var(--brand-navy)]">
            <AlertTriangle className="h-4 w-4 text-amber-600" />
            {t("terminal.activeAlerts")} ({activeAlerts.length})
          </p>
          <ul className="mt-3 space-y-2">
            {activeAlerts.length === 0 ? (
              <li className="text-sm text-[var(--muted)]">{t("terminal.noAlerts")}</li>
            ) : (
              activeAlerts.map((a, i) => (
                <li key={`${a.code}-${i}`} className="rounded-lg border border-[var(--border)] bg-white px-3 py-2 text-sm">
                  {a.message_pt}
                </li>
              ))
            )}
          </ul>
        </div>

        <div className="bank-portal-panel rounded-2xl p-5">
          <p className="text-sm font-bold text-[var(--brand-navy)]">{t("terminal.trendsTitle")}</p>
          <ul className="mt-3 space-y-2 text-sm">
            {(["revenue", "margin", "cash"] as const).map((key) => (
              <li key={key} className="flex items-center justify-between rounded-lg bg-[var(--accent-soft)] px-3 py-2">
                <span>{t(`terminal.trend_${key}`)}</span>
                <span className="flex items-center gap-2 font-medium">
                  {t(`terminal.trend_${terminal.trends[key]}`)}
                  {trendIcon(terminal.trends[key])}
                </span>
              </li>
            ))}
          </ul>
          <p className="mt-4 text-sm font-bold text-[var(--brand-navy)]">{t("terminal.recommendations")}</p>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-[var(--muted)]">
            {(terminal.recommendations ?? []).map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
