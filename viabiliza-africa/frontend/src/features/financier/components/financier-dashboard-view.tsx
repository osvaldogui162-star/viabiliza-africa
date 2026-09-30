"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import type { LucideIcon } from "lucide-react";
import {
  CircleArrowDown,
  ClipboardList,
  Factory,
  HandCoins,
  PieChart,
  ShieldAlert,
  Wallet,
} from "lucide-react";
import { BankDashEmpty } from "@/features/financier/components/bank-dash-empty";
import { BankFinIcon } from "@/features/financier/components/bank-fin-icon";
import { useI18n } from "@/components/providers/locale-provider";
import { DonutChart, FluxoCaixaGroupedChart, SparklineChart } from "@/features/financier/components/financier-charts";
import { FinancierStatusPill } from "@/features/financier/components/financier-status-pill";
import { BankDashCard, BankDashSkeleton } from "@/features/financier/components/bank-dash-card";
import { BankPortalCanvas } from "@/features/financier/components/bank-portal-canvas";
import { FinancierPendingApprovalsPanel } from "@/features/financier/components/financier-pending-approvals-panel";
import { financierApi } from "@/lib/api/financier-api";
import { ApiError } from "@/lib/api/http-client";
import { useAnimatedNumber } from "@/hooks/use-animated-number";
import { useInView } from "@/hooks/use-in-view";
import type { FinancierDashboardResponse } from "@/lib/types/financier";
import { BRAND_COLORS } from "@/lib/constants/brand-colors";
import { cn } from "@/lib/utils/cn";

function CompactKpi({
  label,
  value,
  format,
  currency,
  icon,
  tone,
  active,
  formatMoney,
  delayMs,
}: {
  label: string;
  value: number;
  format: "money" | "int";
  currency?: string;
  icon: LucideIcon;
  tone: "teal" | "rose";
  active: boolean;
  formatMoney: (n: number, c: string) => string;
  delayMs: number;
}) {
  const animated = useAnimatedNumber(value, 1100, active);
  const display =
    format === "money" && currency ? formatMoney(animated, currency) : Math.round(animated).toString();

  return (
    <div
      className={cn(
        "bank-dash-kpi-compact bank-dash-rise",
        tone === "teal" ? "bank-dash-kpi-compact--teal" : "bank-dash-kpi-compact--rose",
      )}
      style={{ animationDelay: `${delayMs}ms` }}
    >
      <BankFinIcon icon={icon} tone={tone} size="md" />
      <div className="min-w-0 flex-1">
        <p className="text-xs font-medium leading-snug text-[var(--muted)]">{label}</p>
        <p className="font-[family-name:var(--font-poppins)] text-lg font-bold tabular-nums tracking-tight text-[var(--brand-navy)] xl:text-[1.35rem]">
          {display}
        </p>
      </div>
    </div>
  );
}

export function FinancierDashboardView() {
  const { t, formatMoney } = useI18n();
  const { ref: gridRef, inView: gridInView } = useInView(0.04);
  const [data, setData] = useState<FinancierDashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      setData(await financierApi.dashboard());
    } catch (e) {
      setError(e instanceof ApiError ? e.message : t("common.error"));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    void load();
    const id = window.setInterval(() => void load(), 120_000);
    return () => window.clearInterval(id);
  }, [load]);

  const s = data?.sections;
  const currency = s?.carteira.currency ?? "AOA";

  const charts =
    data?.charts ??
    (data?.items.length && s
      ? {
          risk_donut: [
            { label: "Em linha", value: s.exposicao.by_risk.on_track ?? 0, color: "#34d399" },
            { label: "Atenção", value: s.exposicao.by_risk.attention ?? 0, color: "#fbbf24" },
            { label: "Crítico", value: s.exposicao.by_risk.critical ?? 0, color: "#f87171" },
          ],
          spend_trend: [] as { month: string; amount: number }[],
        }
      : null);

  const totalExposure = s ? parseFloat(s.carteira.total_exposure) : 0;
  const totalDisbursed = s ? parseFloat(s.desembolsos.total_disbursed) : 0;
  const totalExecuted = s ? parseFloat(s.execucao.total_executed) : 0;
  const pendingDisb = s?.desembolsos.pending_requests ?? 0;
  const alertCount = s?.pendencias.alerts_count ?? 0;
  const pendingApprovals = data?.pending_approvals ?? s?.aprovacoes_pendentes?.items ?? [];

  const executionDonut = s
    ? [
        { label: t("bankPortal.fluxoEntradas"), value: totalDisbursed, color: BRAND_COLORS.teal },
        { label: t("bankPortal.fluxoSaidas"), value: totalExecuted, color: "#f472b6" },
        {
          label: t("bankPortal.sectionPortfolio"),
          value: Math.max(0, totalExposure - totalExecuted),
          color: "#cbd5e1",
        },
      ].filter((x) => x.value > 0)
    : [];

  return (
    <BankPortalCanvas>
      {loading && !data ? <BankDashSkeleton /> : null}

      {error ? (
        <p className="bank-dash-card bank-dash-rise mb-4 px-4 py-3 text-sm text-rose-700">{error}</p>
      ) : null}

      {pendingApprovals.length > 0 ? (
        <FinancierPendingApprovalsPanel items={pendingApprovals} onDecided={() => void load()} compact />
      ) : null}

      {s?.terminal ? (
        <div className="bank-dash-card bank-dash-rise mb-4 grid gap-3 p-4 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <p className="text-xs font-semibold uppercase text-[var(--muted)]">{t("terminal.billingConnected")}</p>
            <p className="text-2xl font-bold tabular-nums text-[var(--brand-navy)]">
              {s.terminal.billing_connected_count}/{s.carteira.projects_count}
            </p>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase text-[var(--muted)]">{t("terminal.avgDeviation")}</p>
            <p className="text-2xl font-bold tabular-nums text-[var(--brand-navy)]">
              {s.terminal.avg_deviation_pct != null ? `${s.terminal.avg_deviation_pct}%` : "—"}
            </p>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase text-[var(--muted)]">{t("terminal.riskLow")}</p>
            <p className="text-2xl font-bold tabular-nums text-emerald-700">{s.terminal.risk_mix.low ?? 0}</p>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase text-[var(--muted)]">{t("terminal.riskHigh")}</p>
            <p className="text-2xl font-bold tabular-nums text-rose-700">{s.terminal.risk_mix.high ?? 0}</p>
          </div>
        </div>
      ) : null}

      {s && charts && data ? (
        <div
          ref={gridRef}
          className={cn("bank-fin-grid", gridInView && "bank-fin-grid--ready")}
        >
          <div className="bank-fin-area-kpis bank-dash-kpi-stack">
            <CompactKpi
              label={t("bankPortal.fluxoEntradas")}
              value={totalDisbursed}
              format="money"
              currency={currency}
              icon={HandCoins}
              tone="teal"
              active={gridInView}
              formatMoney={formatMoney}
              delayMs={60}
            />
            <CompactKpi
              label={t("bankPortal.fluxoSaidas")}
              value={totalExecuted}
              format="money"
              currency={currency}
              icon={CircleArrowDown}
              tone="rose"
              active={gridInView}
              formatMoney={formatMoney}
              delayMs={120}
            />
            <CompactKpi
              label={t("bankPortal.sectionPending")}
              value={alertCount}
              format="int"
              icon={ShieldAlert}
              tone="rose"
              active={gridInView}
              formatMoney={formatMoney}
              delayMs={180}
            />
            <CompactKpi
              label={t("bankPortal.pendingRequests")}
              value={pendingDisb}
              format="int"
              icon={ClipboardList}
              tone="teal"
              active={gridInView}
              formatMoney={formatMoney}
              delayMs={240}
            />
          </div>

          <BankDashCard
            title={t("bankPortal.fluxoCaixa")}
            className="bank-fin-area-flux min-h-[min(420px,55vh)]"
            delayMs={140}
          >
            <FluxoCaixaGroupedChart
              points={charts.spend_trend}
              totalInflow={totalDisbursed}
              formatMoney={(n) => formatMoney(n, currency)}
              active={gridInView}
              inflowLabel={t("bankPortal.fluxoEntradas")}
              outflowLabel={t("bankPortal.fluxoSaidas")}
              emptyHint={t("bankPortal.fluxEmptyHint")}
            />
          </BankDashCard>

          <aside className="bank-fin-area-portfolio bank-dash-side-panel bank-dash-rise xl:min-h-[520px]" style={{ animationDelay: "200ms" }}>
            <div className="bank-dash-side-panel-head">
              <p className="text-xs font-semibold">{t("bankPortal.portfolioBalances")}</p>
              <p className="bank-dash-total mt-1 font-[family-name:var(--font-poppins)] text-2xl font-bold tabular-nums">
                {formatMoney(totalExposure, currency)}
              </p>
              <p className="text-[11px]">
                {s.carteira.projects_count} {t("bankPortal.projects")} · {t("bankPortal.portfolioTotal")}
              </p>
            </div>
            <div className="bank-dash-side-list">
              {data.items.map((item, idx) => (
                <Link
                  key={item.id}
                  href={`/financiador/${item.id}`}
                  className="bank-dash-side-row group"
                  style={{ animationDelay: `${240 + idx * 45}ms` }}
                >
                  <div className="flex min-w-0 items-center gap-3">
                    <BankFinIcon icon={Factory} tone="teal" size="sm" className="ring-0" />
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-[var(--brand-navy)] transition group-hover:text-[var(--brand-teal)]">
                        {item.project_name}
                      </p>
                      <p className="truncate text-xs text-[var(--muted)]">{item.company_name ?? "—"}</p>
                    </div>
                  </div>
                  <div className="shrink-0 text-right">
                    <p className="text-sm font-bold tabular-nums text-[var(--foreground)]">
                      {formatMoney(parseFloat(item.approved_amount), item.currency)}
                    </p>
                    <FinancierStatusPill status={item.monitoring_status} className="mt-1 origin-right scale-90" />
                  </div>
                </Link>
              ))}
              {data.items.length === 0 ? (
                <BankDashEmpty icon={Factory} title={t("financier.emptyTitle")} hint={t("bankPortal.portfolioEmptyHint")} />
              ) : null}
            </div>
            <div className="border-t border-[var(--border)] bg-[var(--card)] p-3">
              <Link
                href="/financiador/projectos"
                className="flex items-center justify-center gap-2 rounded-lg bg-[var(--brand-navy)] py-2.5 text-sm font-semibold text-white shadow-lg transition hover:bg-[var(--brand-teal)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--brand-gold)]"
              >
                <Wallet className="h-4 w-4" />
                {t("bankPortal.viewAllProjects")}
              </Link>
            </div>
          </aside>

          <div className="bank-fin-area-bottom">
            <BankDashCard title={t("bankPortal.chartRiskMix")} delayMs={280} className="h-full">
              {charts.risk_donut.some((x) => x.value > 0) ? (
                <DonutChart
                  slices={charts.risk_donut.filter((x) => x.value > 0)}
                  active={gridInView}
                  theme="light"
                  centerLabel={String(s.carteira.projects_count)}
                />
              ) : (
                <BankDashEmpty icon={PieChart} title={t("financier.emptyTitle")} />
              )}
            </BankDashCard>

            <BankDashCard title={t("bankPortal.sectionExecution")} delayMs={340} className="h-full">
              {executionDonut.length > 0 ? (
                <DonutChart slices={executionDonut} active={gridInView} theme="light" />
              ) : (
                <BankDashEmpty icon={HandCoins} title={t("financier.emptyTitle")} />
              )}
            </BankDashCard>

            <BankDashCard title={t("bankPortal.resultado")} delayMs={400} className="h-full">
              <p className="font-[family-name:var(--font-poppins)] text-2xl font-bold tabular-nums text-[var(--brand-teal)]">
                {formatMoney(totalExecuted, currency)}
              </p>
              <p className="text-xs font-medium text-[var(--muted)]">
                {s.execucao.execution_vs_approved_pct}% {t("bankPortal.vsCredit")}
              </p>
              <SparklineChart points={charts.spend_trend} active={gridInView} />
            </BankDashCard>
          </div>
        </div>
      ) : null}

    </BankPortalCanvas>
  );
}
