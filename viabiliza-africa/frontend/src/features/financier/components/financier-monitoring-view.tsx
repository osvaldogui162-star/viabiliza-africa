"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { ChevronLeft, LineChart, RefreshCw } from "lucide-react";
import { BankPortalCanvas } from "@/features/financier/components/bank-portal-canvas";
import { useAuth } from "@/components/providers/auth-provider";
import { useI18n } from "@/components/providers/locale-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { BankLogoBadge } from "@/features/financier/components/bank-logo-badge";
import { ExecutionChartsPanel } from "@/features/financier/components/execution-charts-panel";
import { TerminalMonitoringPanelView } from "@/features/financier/components/terminal-monitoring-panel";
import { FinancierStatusPill } from "@/features/financier/components/financier-status-pill";
import { PageLoader } from "@/components/ui/spinner";
import { FinancierPendingApprovalsPanel } from "@/features/financier/components/financier-pending-approvals-panel";
import { financierApi } from "@/lib/api/financier-api";
import { ApiError } from "@/lib/api/http-client";
import type { FinancierMonitoringResponse } from "@/lib/types/financier";
import { cn } from "@/lib/utils/cn";

type Tab = "overview" | "financial" | "physical" | "schedule" | "disbursements" | "documents" | "alerts" | "activity";

export function FinancierMonitoringView({ financingId }: { financingId: string }) {
  const { user } = useAuth();
  const { t, formatMoney } = useI18n();
  const [data, setData] = useState<FinancierMonitoringResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("overview");
  const [disbAmount, setDisbAmount] = useState("");
  const [docTitle, setDocTitle] = useState("");

  const load = useCallback(async () => {
    setError(null);
    try {
      setData(await financierApi.monitoring(financingId));
    } catch (e) {
      setError(e instanceof ApiError ? e.message : t("common.error"));
    } finally {
      setLoading(false);
    }
  }, [financingId, t]);

  useEffect(() => {
    void load();
    const id = window.setInterval(() => void load(), 120_000);
    return () => window.clearInterval(id);
  }, [load]);

  const statusLabel =
    data?.monitoring_status === "on_track"
      ? t("financier.statusOnTrack")
      : data?.monitoring_status === "attention"
        ? t("financier.statusAttention")
        : t("financier.statusCritical");

  const tabs: { id: Tab; label: string }[] = [
    { id: "overview", label: t("terminal.tabMonitoring") },
    { id: "financial", label: t("bankPortal.tabFinancial") },
    { id: "physical", label: t("bankPortal.tabPhysical") },
    { id: "schedule", label: t("bankPortal.tabSchedule") },
    { id: "disbursements", label: t("bankPortal.tabDisbursements") },
    { id: "documents", label: t("bankPortal.tabDocuments") },
    { id: "alerts", label: t("bankPortal.tabAlerts") },
    { id: "activity", label: t("bankPortal.tabActivity") },
  ];

  if (loading && !data) {
    return (
      <PageLoader
        message={t("common.loadingProject")}
        layout="section"
        className="min-h-[50vh]"
      />
    );
  }

  const awaitingBank = data?.workflow?.awaiting_bank_decision === true;
  const canDecide = data?.workflow?.can_decide === true;

  if (error || !data) {
    return (
      <div className="mx-auto max-w-lg px-4 py-16 text-center">
        <p className="text-rose-700">{error ?? t("common.error")}</p>
        <Link href="/financiador" className="mt-4 inline-block text-sm font-semibold text-[var(--brand-teal)]">
          {t("financier.backPortfolio")}
        </Link>
      </div>
    );
  }

  async function requestDisbursement() {
    if (!disbAmount) return;
    await financierApi.createDisbursement(financingId, { requested_amount: disbAmount });
    setDisbAmount("");
    await load();
  }

  async function uploadDoc() {
    if (!docTitle.trim()) return;
    await financierApi.createDocument(financingId, { doc_type: "other", title: docTitle.trim() });
    setDocTitle("");
    await load();
  }

  return (
    <BankPortalCanvas>
      <header className="bank-dash-card bank-dash-rise mb-4 p-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex min-w-0 items-center gap-3">
            <Link
              href="/financiador/projectos"
              className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-[var(--border)] text-[var(--muted)] transition hover:bg-[var(--accent-soft)]"
              aria-label={t("financier.backPortfolio")}
            >
              <ChevronLeft className="h-5 w-5" />
            </Link>
            <BankLogoBadge bank={data.financing.bank} size="md" />
            <div className="min-w-0">
              <p className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-[0.18em] text-[var(--brand-teal)]">
                <LineChart className="h-3.5 w-3.5" />
                {t("bankPortal.tabOverview")}
              </p>
              <h1 className="truncate font-[family-name:var(--font-poppins)] text-xl font-bold text-[var(--brand-navy)] sm:text-2xl">
                {data.project.name}
              </h1>
              <p className="truncate text-sm text-[var(--muted)]">
                {data.project.company_name ?? "—"} · {data.project.sector_label ?? ""}
              </p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <FinancierStatusPill status={data.monitoring_status} label={statusLabel} />
            <button
              type="button"
              onClick={() => void load()}
              className="va-btn-secondary inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold"
            >
              <RefreshCw className="h-4 w-4" />
              {t("financier.refresh")}
            </button>
          </div>
        </div>
      </header>

      {awaitingBank ? (
        <div className="bank-dash-card bank-dash-rise mb-4 border border-amber-200 bg-amber-50/70 p-4 text-sm text-amber-950">
          {t("financier.pendingRequestBanner")}
        </div>
      ) : null}

      {awaitingBank && canDecide ? (
        <FinancierPendingApprovalsPanel items={[data.financing]} onDecided={() => void load()} />
      ) : null}

      {!awaitingBank ? (
      <>
      <div className="bank-dash-card mb-4 overflow-x-auto px-2 py-2">
        <div className="flex min-w-max gap-1">
          {tabs.map(({ id, label }) => (
            <button
              key={id}
              type="button"
              onClick={() => setTab(id)}
              className={cn(
                "bank-portal-nav-link shrink-0 rounded-full px-3.5 py-2 text-xs font-semibold sm:text-sm",
                tab === id
                  ? "bg-[var(--brand-teal)] text-white shadow-md"
                  : "text-[var(--muted)] hover:bg-[var(--accent-soft)] hover:text-[var(--brand-navy)]",
              )}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      <div className="max-w-6xl">
        {tab === "overview" && data.terminal ? (
          <TerminalMonitoringPanelView terminal={data.terminal} />
        ) : null}
        {tab === "overview" && !data.terminal ? (
          <p className="text-sm text-[var(--muted)]">{t("terminal.awaitingBilling")}</p>
        ) : null}
        {tab === "financial" ? <ExecutionChartsPanel data={data} theme="light" /> : null}

        {tab === "physical" ? (
          <div className="bank-portal-panel rounded-2xl p-6">
            <p className="text-3xl font-bold tabular-nums text-[var(--brand-navy)]">{data.physical?.progress_pct ?? 0}%</p>
            <p className="text-sm text-[var(--muted)]">{t("bankPortal.physicalHint")}</p>
          </div>
        ) : null}

        {tab === "schedule" ? (
          <ul className="space-y-2">
            {(data.schedule?.milestones as { title: string; due_date: string | null; status: string }[] | undefined)?.map(
              (m, i) => (
                <li
                  key={i}
                  className="bank-portal-panel rounded-xl px-4 py-3 text-sm"
                >
                  <p className="font-semibold">{m.title}</p>
                  <p className="text-xs text-[var(--muted)]">
                    {m.due_date ?? "—"} · {m.status}
                  </p>
                </li>
              ),
            )}
          </ul>
        ) : null}

        {tab === "disbursements" ? (
          <div className="space-y-4">
            {user?.role !== "bank" ? (
              <div className="flex flex-wrap gap-2">
                <Input
                  placeholder={t("bankPortal.amount")}
                  value={disbAmount}
                  onChange={(e) => setDisbAmount(e.target.value)}
                  className="max-w-xs"
                />
                <Button onClick={() => void requestDisbursement()}>{t("bankPortal.requestDisbursement")}</Button>
              </div>
            ) : null}
            <ul className="space-y-2">
              {data.disbursements?.map((d) => (
                <li
                  key={d.id}
                  className="bank-portal-panel rounded-xl px-4 py-3 text-sm"
                >
                  {formatMoney(parseFloat(d.requested_amount), d.currency)} — {d.status}
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        {tab === "documents" ? (
          <div className="space-y-4">
            <div className="flex flex-wrap gap-2">
              <Input
                placeholder={t("bankPortal.docTitle")}
                value={docTitle}
                onChange={(e) => setDocTitle(e.target.value)}
                className="max-w-sm"
              />
              <Button onClick={() => void uploadDoc()}>{t("bankPortal.registerDoc")}</Button>
            </div>
            <ul className="space-y-2">
              {data.documents?.map((doc) => (
                <li
                  key={doc.id}
                  className="bank-portal-panel rounded-xl px-4 py-3 text-sm"
                >
                  {doc.title} · {doc.validation_status}
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        {tab === "alerts" ? (
          <ul className="space-y-2">
            {data.alerts?.map((a, i) => (
              <li
                key={i}
                className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950"
              >
                {a.message_pt}
              </li>
            ))}
          </ul>
        ) : null}

        {tab === "activity" ? (
          <ol className="space-y-3">
            {data.activity?.map((ev) => (
              <li key={ev.id} className="text-sm text-[var(--foreground)]">
                <time className="text-xs opacity-70">{new Date(ev.created_at).toLocaleString()}</time>
                <p>
                  {ev.actor_name} — {ev.summary}
                </p>
              </li>
            ))}
          </ol>
        ) : null}
      </div>
      </>
      ) : (
        <div className="max-w-6xl">
          <ol className="space-y-3">
            {data.activity?.map((ev) => (
              <li key={ev.id} className="text-sm text-[var(--foreground)]">
                <time className="text-xs opacity-70">{new Date(ev.created_at).toLocaleString()}</time>
                <p>
                  {ev.actor_name} — {ev.summary}
                </p>
              </li>
            ))}
          </ol>
        </div>
      )}
    </BankPortalCanvas>
  );
}
