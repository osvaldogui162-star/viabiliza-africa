"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { ArrowRight, FolderKanban } from "lucide-react";
import { useI18n } from "@/components/providers/locale-provider";
import { BankPortalCanvas } from "@/features/financier/components/bank-portal-canvas";
import { FinancierStatusPill } from "@/features/financier/components/financier-status-pill";
import { PageLoader } from "@/components/ui/spinner";
import { financierApi } from "@/lib/api/financier-api";
import { ApiError } from "@/lib/api/http-client";
import type { FinancingListItem } from "@/lib/types/financier";

export function FinancierProjectsTable() {
  const { t, formatMoney } = useI18n();
  const [items, setItems] = useState<FinancingListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await financierApi.portfolio();
      setItems(res.items);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : t("common.error"));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    void load();
  }, [load]);

  const statusLabel = (s: FinancingListItem["monitoring_status"]) => {
    if (s === "on_track") return t("financier.statusOnTrack");
    if (s === "attention") return t("financier.statusAttention");
    return t("financier.statusCritical");
  };

  return (
    <BankPortalCanvas>
      <header className="bank-dash-card bank-dash-rise mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="flex items-center gap-2 text-sm font-medium text-[var(--brand-teal)]">
            <FolderKanban className="h-4 w-4" />
            {t("bankPortal.navProjects")}
          </p>
          <h1 className="bank-dash-card-title mt-2 text-2xl">{t("bankPortal.projectsTitle")}</h1>
          <p className="mt-2 max-w-xl text-sm leading-relaxed text-[var(--muted)]">{t("terminal.projectsSubtitle")}</p>
        </div>
        {!loading ? (
          <div className="rounded-2xl bg-[var(--accent-soft)] px-5 py-3 text-center">
            <p className="text-3xl font-bold tabular-nums text-[var(--brand-navy)]">{items.length}</p>
            <p className="text-[10px] font-bold uppercase tracking-wide text-[var(--muted)]">{t("bankPortal.projects")}</p>
          </div>
        ) : null}
      </header>
        {loading ? <PageLoader message={t("common.loadingProjects")} layout="section" /> : null}
        {error ? <p className="text-sm text-rose-700">{error}</p> : null}

        <div className="bank-portal-panel overflow-hidden rounded-2xl">
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm text-[var(--foreground)]">
              <thead className="border-b border-[var(--border)] bg-[var(--accent-soft)] text-xs uppercase tracking-wide text-[var(--muted)]">
                <tr>
                  <th className="px-4 py-3">{t("bankPortal.colProject")}</th>
                  <th className="px-4 py-3">{t("terminal.colSector")}</th>
                  <th className="px-4 py-3">{t("terminal.colFinanced")}</th>
                  <th className="px-4 py-3">{t("bankPortal.colStatus")}</th>
                  <th className="px-4 py-3">{t("terminal.colDeviation")}</th>
                  <th className="px-4 py-3">{t("terminal.colRisk")}</th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border)]">
                {items.map((row, i) => (
                  <tr
                    key={row.id}
                    className="bank-dash-rise transition hover:bg-[var(--accent-soft)]/50"
                    style={{ animationDelay: `${Math.min(i, 12) * 35}ms` }}
                  >
                    <td className="px-4 py-3">
                      <p className="font-semibold text-[var(--brand-navy)]">{row.project_name}</p>
                      <p className="text-xs text-[var(--muted)]">{row.company_name ?? "—"}</p>
                    </td>
                    <td className="px-4 py-3 text-sm capitalize text-[var(--muted)]">{row.sector}</td>
                    <td className="px-4 py-3 tabular-nums font-medium">
                      {formatMoney(parseFloat(row.approved_amount), row.currency)}
                    </td>
                    <td className="px-4 py-3">
                      <FinancierStatusPill status={row.monitoring_status} label={statusLabel(row.monitoring_status)} />
                    </td>
                    <td
                      className={`px-4 py-3 tabular-nums text-sm font-bold ${
                        row.deviation_pct != null && row.deviation_pct < 0 ? "text-rose-700" : "text-emerald-700"
                      }`}
                    >
                      {row.deviation_pct != null ? `${row.deviation_pct > 0 ? "+" : ""}${row.deviation_pct}%` : "—"}
                    </td>
                    <td className="px-4 py-3 text-xs font-bold uppercase">
                      {row.risk_level === "high"
                        ? t("terminal.riskHigh")
                        : row.risk_level === "medium"
                          ? t("terminal.riskMedium")
                          : row.risk_level === "low"
                            ? t("terminal.riskLow")
                            : "—"}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Link
                        href={`/financiador/${row.id}`}
                        className="inline-flex items-center gap-1 rounded-full bg-[var(--accent-soft)] px-3 py-1.5 text-xs font-semibold text-[var(--brand-teal)] transition hover:bg-[var(--accent-border)]/30"
                      >
                        {t("bankPortal.open")}
                        <ArrowRight className="h-3.5 w-3.5" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {!loading && items.length === 0 ? (
            <p className="px-4 py-16 text-center text-[var(--muted)]">{t("financier.emptyTitle")}</p>
          ) : null}
        </div>
    </BankPortalCanvas>
  );
}
