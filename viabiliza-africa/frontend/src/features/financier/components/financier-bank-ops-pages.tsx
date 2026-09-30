"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import type { LucideIcon } from "lucide-react";
import {
  AlertTriangle,
  Bell,
  Clock,
  Download,
  FileCheck,
  FileText,
  History,
  Receipt,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { useAuth } from "@/components/providers/auth-provider";
import { useI18n } from "@/components/providers/locale-provider";
import { Button } from "@/components/ui/button";
import { PageLoader } from "@/components/ui/spinner";
import { BankPortalCanvas } from "@/features/financier/components/bank-portal-canvas";
import { financierApi } from "@/lib/api/financier-api";
import { ApiError } from "@/lib/api/http-client";
import type {
  FinancierActivityItem,
  FinancierAlert,
  FinancierDisbursement,
  FinancierDocument,
} from "@/lib/types/financier";
import { cn } from "@/lib/utils/cn";

function PageShell({
  title,
  subtitle,
  eyebrow,
  icon,
  children,
}: {
  title: string;
  subtitle: string;
  eyebrow: string;
  icon: LucideIcon;
  children: React.ReactNode;
}) {
  const Icon = icon;
  return (
    <BankPortalCanvas>
      <header className="bank-dash-card bank-dash-rise mb-6">
        <p className="flex items-center gap-2 text-sm font-medium text-[var(--brand-teal)]">
          <Icon className="h-4 w-4" />
          {eyebrow}
        </p>
        <h1 className="bank-dash-card-title mt-2 text-2xl">{title}</h1>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-[var(--muted)]">{subtitle}</p>
      </header>
      {children}
    </BankPortalCanvas>
  );
}

function severityTone(severity: string) {
  const s = severity.toLowerCase();
  if (s.includes("crit") || s.includes("high")) return "text-rose-700 bg-rose-50 ring-rose-200/80";
  if (s.includes("warn") || s.includes("med")) return "text-amber-800 bg-amber-50 ring-amber-200/80";
  return "text-sky-800 bg-sky-50 ring-sky-200/80";
}

export function FinancierAlertsPage() {
  const { t } = useI18n();
  const [items, setItems] = useState<FinancierAlert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void financierApi.alerts().then((r) => setItems(r.items)).finally(() => setLoading(false));
  }, []);

  return (
    <PageShell
      eyebrow={t("bankPortal.navAlerts")}
      icon={AlertTriangle}
      title={t("bankPortal.alertsTitle")}
      subtitle={t("bankPortal.alertsSubtitle")}
    >
      {loading ? <PageLoader layout="compact" message={t("common.loading")} /> : null}
      <ul className="space-y-3">
        {items.map((a, i) => (
          <li key={`${a.code}-${i}`} className="bank-portal-list-card bank-dash-rise flex gap-3" style={{ animationDelay: `${i * 40}ms` }}>
            <div className="bank-portal-icon-tile shrink-0">
              <Bell className="h-5 w-5" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <span className={cn("rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase ring-1", severityTone(a.severity))}>
                  {a.severity}
                </span>
                {a.project_name && a.financing_id ? (
                  <Link href={`/financiador/${a.financing_id}`} className="font-semibold text-[var(--brand-teal)] hover:underline">
                    {a.project_name}
                  </Link>
                ) : null}
              </div>
              <p className="mt-1.5 text-sm leading-relaxed text-[var(--foreground)]">{a.message_pt}</p>
            </div>
          </li>
        ))}
      </ul>
      {!loading && items.length === 0 ? <Empty msg={t("bankPortal.noAlerts")} icon={ShieldCheck} /> : null}
    </PageShell>
  );
}

export function FinancierDisbursementsPage() {
  const { t, formatMoney } = useI18n();
  const { user } = useAuth();
  const [items, setItems] = useState<FinancierDisbursement[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setItems((await financierApi.disbursements()).items);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const canReview = user?.role === "bank" || user?.role === "admin";

  async function advance(id: string, status: string) {
    try {
      await financierApi.updateDisbursement(id, { status });
      await load();
    } catch (e) {
      alert(e instanceof ApiError ? e.message : t("common.error"));
    }
  }

  const statusLabel: Record<string, string> = {
    requested: t("bankPortal.disbRequested"),
    under_review: t("bankPortal.disbReview"),
    approved: t("bankPortal.disbApproved"),
    paid: t("bankPortal.disbPaid"),
    rejected: t("bankPortal.disbRejected"),
  };

  return (
    <PageShell
      eyebrow={t("bankPortal.navDisbursements")}
      icon={Receipt}
      title={t("bankPortal.disbTitle")}
      subtitle={t("bankPortal.disbSubtitle")}
    >
      {loading ? <PageLoader layout="compact" message={t("common.loading")} /> : null}
      <div className="bank-portal-panel overflow-hidden rounded-2xl">
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm text-[var(--foreground)]">
            <thead className="border-b border-[var(--border)] bg-[var(--accent-soft)] text-xs uppercase tracking-wide text-[var(--muted)]">
              <tr>
                <th className="px-4 py-3 text-left">{t("bankPortal.colProject")}</th>
                <th className="px-4 py-3 text-left">{t("bankPortal.amount")}</th>
                <th className="px-4 py-3 text-left">{t("bankPortal.colStatus")}</th>
                <th className="px-4 py-3 text-left">{t("bankPortal.history")}</th>
                {canReview ? <th className="px-4 py-3" /> : null}
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border)]">
              {items.map((d) => (
                <tr key={d.id} className="transition hover:bg-[var(--accent-soft)]/40">
                  <td className="px-4 py-3">
                    <Link href={`/financiador/${d.financing_id}`} className="inline-flex items-center gap-2 font-medium text-[var(--brand-teal)] hover:underline">
                      <Receipt className="h-4 w-4 opacity-70" />
                      {d.project_name}
                    </Link>
                  </td>
                  <td className="px-4 py-3 tabular-nums font-semibold">
                    {formatMoney(parseFloat(d.requested_amount), d.currency)}
                  </td>
                  <td className="px-4 py-3">
                    <span className="rounded-full bg-[var(--accent-soft)] px-2.5 py-1 text-xs font-semibold text-[var(--brand-navy)]">
                      {statusLabel[d.status] ?? d.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-[var(--muted)]">
                    <span className="inline-flex items-center gap-1">
                      <Clock className="h-3.5 w-3.5" />
                      {new Date(d.requested_at).toLocaleDateString()}
                    </span>
                    {d.paid_at ? ` · ${t("bankPortal.disbPaid")} ${new Date(d.paid_at).toLocaleDateString()}` : ""}
                  </td>
                  {canReview ? (
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1">
                        {d.status === "requested" ? (
                          <Button size="sm" variant="secondary" onClick={() => void advance(d.id, "under_review")}>
                            {t("bankPortal.analyse")}
                          </Button>
                        ) : null}
                        {d.status === "under_review" ? (
                          <>
                            <Button size="sm" onClick={() => void advance(d.id, "approved")}>
                              {t("bankPortal.approve")}
                            </Button>
                            <Button size="sm" variant="secondary" onClick={() => void advance(d.id, "rejected")}>
                              {t("bankPortal.reject")}
                            </Button>
                          </>
                        ) : null}
                        {d.status === "approved" ? (
                          <Button size="sm" onClick={() => void advance(d.id, "paid")}>
                            {t("bankPortal.markPaid")}
                          </Button>
                        ) : null}
                      </div>
                    </td>
                  ) : null}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      {!loading && items.length === 0 ? <Empty msg={t("bankPortal.noDisbursements")} icon={Receipt} /> : null}
    </PageShell>
  );
}

export function FinancierDocumentsPage() {
  const { t } = useI18n();
  const { user } = useAuth();
  const [items, setItems] = useState<FinancierDocument[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setItems((await financierApi.documents()).items);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const canValidate = user?.role === "bank" || user?.role === "admin";

  async function validate(id: string, validation_status: "valid" | "rejected") {
    await financierApi.validateDocument(id, { validation_status });
    await load();
  }

  return (
    <PageShell
      eyebrow={t("bankPortal.navDocuments")}
      icon={FileText}
      title={t("bankPortal.docsTitle")}
      subtitle={t("bankPortal.docsSubtitle")}
    >
      {loading ? <PageLoader layout="compact" message={t("common.loading")} /> : null}
      <ul className="space-y-3">
        {items.map((doc, i) => (
          <li
            key={doc.id}
            className="bank-portal-list-card bank-dash-rise flex flex-wrap items-center justify-between gap-3"
            style={{ animationDelay: `${i * 40}ms` }}
          >
            <div className="flex min-w-0 items-start gap-3">
              <div className="bank-portal-icon-tile shrink-0">
                <FileCheck className="h-5 w-5" />
              </div>
              <div>
                <p className="font-semibold text-[var(--foreground)]">{doc.title}</p>
                <p className="mt-0.5 text-xs text-[var(--muted)]">
                  {doc.project_name} · {doc.doc_type} · {doc.validation_status}
                </p>
              </div>
            </div>
            {canValidate && doc.validation_status === "pending" ? (
              <div className="flex gap-2">
                <Button size="sm" onClick={() => void validate(doc.id, "valid")}>
                  {t("bankPortal.validate")}
                </Button>
                <Button size="sm" variant="secondary" onClick={() => void validate(doc.id, "rejected")}>
                  {t("bankPortal.rejectDoc")}
                </Button>
              </div>
            ) : null}
          </li>
        ))}
      </ul>
      {!loading && items.length === 0 ? <Empty msg={t("bankPortal.noDocuments")} icon={FileText} /> : null}
    </PageShell>
  );
}

export function FinancierActivityPage() {
  const { t } = useI18n();
  const [items, setItems] = useState<FinancierActivityItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void financierApi.activity(80).then((r) => setItems(r.items)).finally(() => setLoading(false));
  }, []);

  return (
    <PageShell
      eyebrow={t("bankPortal.navActivity")}
      icon={History}
      title={t("bankPortal.activityTitle")}
      subtitle={t("bankPortal.activitySubtitle")}
    >
      {loading ? <PageLoader layout="compact" message={t("common.loading")} /> : null}
      <ol className="relative ms-2 border-s-2 border-[var(--brand-teal)]/25 ps-6">
        {items.map((ev, i) => (
          <li key={ev.id} className="bank-dash-rise relative mb-8 last:mb-0" style={{ animationDelay: `${i * 35}ms` }}>
            <span className="absolute -start-[1.65rem] top-1 flex h-4 w-4 items-center justify-center rounded-full bg-[var(--brand-teal)] ring-4 ring-[var(--background)]">
              <Sparkles className="h-2.5 w-2.5 text-white" />
            </span>
            <time className="text-xs font-medium text-[var(--muted)]">{new Date(ev.created_at).toLocaleString()}</time>
            <p className="mt-1 text-sm text-[var(--foreground)]">
              <strong className="text-[var(--brand-navy)]">{ev.actor_name ?? "—"}</strong> — {ev.summary}
            </p>
          </li>
        ))}
      </ol>
      {!loading && items.length === 0 ? <Empty msg={t("bankPortal.noActivity")} icon={History} /> : null}
    </PageShell>
  );
}

export function FinancierReportsPage() {
  const { t } = useI18n();
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [reportKind, setReportKind] = useState<"portfolio" | "credit">("portfolio");
  const [loading, setLoading] = useState(false);

  async function generate(kind: "portfolio" | "credit") {
    setLoading(true);
    try {
      const res =
        kind === "credit" ? await financierApi.creditReport() : await financierApi.portfolioReport();
      setRows(res.rows);
      setReportKind(kind);
    } finally {
      setLoading(false);
    }
  }

  function downloadCsv() {
    if (!rows.length) return;
    const headers = Object.keys(rows[0]);
    const lines = [headers.join(";"), ...rows.map((r) => headers.map((h) => String(r[h] ?? "")).join(";"))];
    const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    const prefix = reportKind === "credit" ? "relatorio-credito-terminal" : "carteira-financiador";
    a.download = `${prefix}-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <PageShell
      eyebrow={t("bankPortal.navReports")}
      icon={Download}
      title={t("bankPortal.reportsTitle")}
      subtitle={t("terminal.creditReportSubtitle")}
    >
      <div className="bank-portal-stat-card flex flex-wrap items-center gap-3">
        <Button onClick={() => void generate("portfolio")} disabled={loading} className="gap-2">
          <Download className="h-4 w-4" />
          {loading && reportKind === "portfolio" ? t("common.loading") : t("bankPortal.generateReport")}
        </Button>
        <Button onClick={() => void generate("credit")} disabled={loading} variant="secondary" className="gap-2">
          <Download className="h-4 w-4" />
          {loading && reportKind === "credit" ? t("common.loading") : t("terminal.generateCreditReport")}
        </Button>
        <Button variant="secondary" onClick={downloadCsv} disabled={!rows.length} className="gap-2">
          <FileText className="h-4 w-4" />
          {t("bankPortal.downloadCsv")}
        </Button>
      </div>
      {rows.length ? (
        <p className="mt-4 flex items-center gap-2 text-sm text-[var(--muted)]">
          <ShieldCheck className="h-4 w-4 text-[var(--brand-teal)]" />
          {t("bankPortal.reportReady")}: {rows.length} {t("bankPortal.rows")}
        </p>
      ) : null}
    </PageShell>
  );
}

function Empty({ msg, icon: Icon }: { msg: string; icon: LucideIcon }) {
  return (
    <div className="bank-portal-panel flex flex-col items-center gap-3 rounded-2xl py-16 text-center">
      <div className="bank-portal-icon-tile h-14 w-14">
        <Icon className="h-7 w-7" />
      </div>
      <p className="text-sm text-[var(--muted)]">{msg}</p>
    </div>
  );
}
