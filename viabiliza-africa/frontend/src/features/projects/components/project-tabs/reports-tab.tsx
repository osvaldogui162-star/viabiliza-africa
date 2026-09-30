"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import {
  Download,
  FileText,
  Mail,
  MessageCircle,
  Plus,
  Printer,
  Send,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardHeader } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { PageLoader } from "@/components/ui/spinner";
import { Select } from "@/components/ui/select";
import { useAuth } from "@/components/providers/auth-provider";
import { useI18n } from "@/components/providers/locale-provider";
import { ApiError } from "@/lib/api/http-client";
import { ingestionApi } from "@/lib/api/ingestion-api";
import { reportsApi } from "@/lib/api/reports-api";
import { formatDateTime } from "@/lib/utils/format";
import type { AuditTrailEntry } from "@/lib/types/ingestion";
import type { Report, ReportType } from "@/lib/types/reports";
import type { Project } from "@/lib/types/project";
import { SendReportEmailModal } from "./send-report-email-modal";
import { ProjectScrollPanel } from "@/features/projects/components/project-scroll-panel";
import { useMySubscription } from "@/hooks/use-my-subscription";
import type { PlanCapabilities } from "@/lib/types/subscription";

type ActionModal = "whatsapp" | "bank" | null;

function reportTypeAllowed(type: ReportType, cap: PlanCapabilities | null, isAdmin: boolean): boolean {
  if (isAdmin) return true;
  if (!cap) return type === "international";
  if (type === "international") return cap.reports_international;
  if (type === "bfa") return cap.reports_bfa;
  if (type === "bda") return cap.reports_bda;
  return false;
}

export function ReportsTab({ project }: { project: Project }) {
  const { user } = useAuth();
  const { t, locale, intlLocale, currency: displayCurrency } = useI18n();
  const { capabilities } = useMySubscription(user?.role !== "admin");
  const isAdmin = user?.role === "admin";
  const bankApiAllowed = isAdmin || capabilities?.bank_api_enabled === true;
  const canSendEmail =
    user?.role === "admin" || (user?.role === "financial" && project.is_owner);

  const reportTypes = useMemo((): { value: ReportType; label: string }[] => {
    const all: { value: ReportType; label: string }[] = [
      { value: "international", label: t("reports.types.international") },
      { value: "bfa", label: t("reports.types.bfa") },
      { value: "bda", label: t("reports.types.bda") },
    ];
    return all.filter((item) => reportTypeAllowed(item.value, capabilities, isAdmin));
  }, [t, capabilities, isAdmin]);

  const [reports, setReports] = useState<Report[]>([]);
  const [emailHistory, setEmailHistory] = useState<AuditTrailEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [generateModal, setGenerateModal] = useState(false);
  const [emailModalOpen, setEmailModalOpen] = useState(false);
  const [actionModal, setActionModal] = useState<ActionModal>(null);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [generating, setGenerating] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [reportType, setReportType] = useState<ReportType>("international");
  const [language, setLanguage] = useState(locale);
  const [reportCurrency, setReportCurrency] = useState(displayCurrency);
  const [whatsappPhone, setWhatsappPhone] = useState("");
  const [bankCode, setBankCode] = useState<"bfa" | "bda">("bfa");

  useEffect(() => {
    setLanguage(locale);
  }, [locale]);

  useEffect(() => {
    if (reportTypes.length === 0) return;
    if (!reportTypes.some((item) => item.value === reportType)) {
      setReportType(reportTypes[0]!.value);
    }
  }, [reportTypes, reportType]);

  useEffect(() => {
    if (reportType === "bfa") {
      setReportCurrency("AOA");
    } else if (reportType === "bda") {
      setReportCurrency("USD");
    } else {
      setReportCurrency(displayCurrency);
    }
  }, [reportType, displayCurrency]);

  const loadEmailHistory = useCallback(async () => {
    if (!canSendEmail) {
      setEmailHistory([]);
      return;
    }
    try {
      const res = await ingestionApi.getAuditTrail(project.id);
      const items = (res.items ?? []).filter(
        (entry) => entry.action === "report_sent_email",
      );
      setEmailHistory(items.slice(0, 8));
    } catch {
      setEmailHistory([]);
    }
  }, [canSendEmail, project.id]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await reportsApi.list(project.id);
      setReports(res.items);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("reports.loadError"));
    } finally {
      setLoading(false);
    }
  }, [project.id, t]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    void loadEmailHistory();
  }, [loadEmailHistory]);

  async function handleGenerate() {
    setGenerating(true);
    try {
      await reportsApi.generate(project.id, {
        report_type: reportType,
        language,
        currency: reportCurrency,
      });
      toast.success(t("reports.generateSuccess"));
      setGenerateModal(false);
      void load();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("reports.generateError"));
    } finally {
      setGenerating(false);
    }
  }

  async function handleDownload(reportId: string) {
    try {
      const { blob, filename } = await reportsApi.download(project.id, reportId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("reports.downloadError"));
    }
  }

  async function handlePrint(reportId: string) {
    try {
      const { blob } = await reportsApi.print(project.id, reportId);
      const url = URL.createObjectURL(blob);
      const win = window.open(url, "_blank");
      if (win) {
        win.onload = () => {
          win.focus();
          win.print();
        };
      }
      toast.success(t("reports.printSuccess"));
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("reports.printError"));
    }
  }

  function openEmail(report: Report) {
    if (!canSendEmail) {
      toast.error(t("reports.noPermissionEmail"));
      return;
    }
    setSelectedReport(report);
    setEmailModalOpen(true);
  }

  function openAction(report: Report, action: ActionModal) {
    setSelectedReport(report);
    setActionModal(action);
    setWhatsappPhone("");
  }

  async function handleShareWhatsApp() {
    if (!selectedReport) return;
    setSubmitting(true);
    try {
      const result = await reportsApi.shareWhatsApp(
        project.id,
        selectedReport.id,
        whatsappPhone || undefined,
      );
      const targetUrl = result.whatsapp_url ?? result.share_url;
      if (targetUrl) {
        window.open(targetUrl, "_blank", "noopener,noreferrer");
      }
      toast.success(t("reports.shareSuccess"));
      setActionModal(null);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("reports.shareError"));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleSubmitBank() {
    if (!selectedReport) return;
    setSubmitting(true);
    try {
      const result = await reportsApi.submitToBank(project.id, selectedReport.id, bankCode);
      toast.success(result.message ?? t("reports.submitSuccess", { bank: bankCode.toUpperCase() }));
      setActionModal(null);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("reports.submitError"));
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <PageLoader />;

  return (
    <div className="space-y-4">
      <div className="va-project-hero overflow-hidden rounded-2xl border border-teal-900/10 px-5 py-5 sm:px-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-teal-700">
              {t("reports.module")}
            </p>
            <h2 className="mt-1 text-xl font-bold tracking-tight text-zinc-900 sm:text-2xl">
              {t("reports.title")}
            </h2>
            <p className="mt-2 max-w-xl text-sm leading-relaxed text-zinc-600">
              {t("reports.description")}
            </p>
          </div>
          <Button onClick={() => setGenerateModal(true)} className="shrink-0 shadow-sm">
            <Plus className="h-4 w-4" /> {t("reports.generate")}
          </Button>
        </div>
        {!isAdmin && reportTypes.length < 3 ? (
          <p className="mt-3 text-xs text-amber-700">
            {locale === "en"
              ? "BFA and BDA reports require Starter or higher."
              : "Relatórios BFA e BDA exigem plano Starter ou superior."}{" "}
            <a href="/planos" className="underline">
              /planos
            </a>
          </p>
        ) : null}
      </div>

      <div className="grid gap-4 xl:grid-cols-12">
        <Card variant="panel" className="xl:col-span-7">
          <CardHeader
            eyebrow={t("projectTabs.reports")}
            title={t("reports.generated")}
            description={t("reports.documentsAvailable", { count: reports.length })}
          />
          {reports.length === 0 ? (
            <EmptyState
              compact
              title={t("reports.empty")}
              description={t("reports.emptyDescription")}
              action={
                <Button size="sm" onClick={() => setGenerateModal(true)}>
                  <Plus className="h-4 w-4" /> {t("reports.generate")}
                </Button>
              }
            />
          ) : (
            <ProjectScrollPanel maxHeight="max-h-[min(52vh,500px)]">
              <ul className="divide-y divide-zinc-100">
                {reports.map((report) => (
                  <li
                    key={report.id}
                    className="flex flex-wrap items-center justify-between gap-3 px-3 py-3 text-sm transition hover:bg-zinc-50/80"
                  >
                    <div className="flex min-w-0 items-center gap-3">
                      <div className="rounded-xl border border-teal-100 bg-teal-50 p-2.5">
                        <FileText className="h-5 w-5 text-teal-700" />
                      </div>
                      <div className="min-w-0">
                        <p className="truncate font-semibold text-zinc-900">
                          {report.title || report.report_type_label}
                        </p>
                        <p className="text-xs text-zinc-500">
                          {report.report_type_label} · {report.language.toUpperCase()} ·{" "}
                          {report.currency} · {formatDateTime(report.created_at, intlLocale)}
                        </p>
                      </div>
                    </div>
                    <div className="flex flex-wrap items-center gap-1.5">
                      <Badge variant={report.status === "ready" ? "success" : "default"}>
                        {report.status}
                      </Badge>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => void handleDownload(report.id)}
                        title={t("common.download")}
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => void handlePrint(report.id)}
                        title={t("common.print")}
                      >
                        <Printer className="h-4 w-4" />
                      </Button>
                      {report.status === "ready" && canSendEmail ? (
                        <>
                          <Button
                            variant="secondary"
                            size="sm"
                            onClick={() => openEmail(report)}
                            title={t("reports.sendEmail")}
                          >
                            <Mail className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => openAction(report, "whatsapp")}
                            title="WhatsApp"
                          >
                            <MessageCircle className="h-4 w-4" />
                          </Button>
                          {bankApiAllowed &&
                          (report.report_type === "bfa" || report.report_type === "bda") ? (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => openAction(report, "bank")}
                              title={t("reports.submitBank")}
                            >
                              <Send className="h-4 w-4" />
                            </Button>
                          ) : null}
                        </>
                      ) : null}
                    </div>
                  </li>
                ))}
              </ul>
            </ProjectScrollPanel>
          )}
        </Card>

        {canSendEmail ? (
          <Card variant="panel" className="xl:col-span-5">
            <CardHeader
              eyebrow={t("reports.emailHistory")}
              title={t("reports.emailHistory")}
              description={t("reports.emailHistoryDesc")}
            />
            {emailHistory.length === 0 ? (
              <EmptyState compact title={t("reports.noEmails")} />
            ) : (
              <ProjectScrollPanel maxHeight="max-h-[min(52vh,500px)]">
                <ul className="divide-y divide-zinc-100">
                  {emailHistory.map((entry) => {
                    const meta = (entry.metadata ?? {}) as Record<string, unknown>;
                    const to =
                      (typeof meta.recipient === "string" && meta.recipient) ||
                      (typeof meta.to === "string" && meta.to) ||
                      "—";
                    const subject =
                      typeof meta.subject === "string" ? meta.subject : t("common.report");
                    return (
                      <li
                        key={entry.id}
                        className="flex flex-wrap items-start justify-between gap-3 px-3 py-3 text-sm"
                      >
                        <div className="flex min-w-0 items-start gap-2.5">
                          <div className="rounded-lg bg-teal-50 p-2 text-teal-700">
                            <Mail className="h-4 w-4" />
                          </div>
                          <div className="min-w-0">
                            <p className="truncate font-semibold text-zinc-900">{to}</p>
                            <p className="truncate text-xs text-zinc-500">{subject}</p>
                          </div>
                        </div>
                        <p className="shrink-0 text-[10px] text-zinc-400">
                          {formatDateTime(entry.created_at, intlLocale)}
                        </p>
                      </li>
                    );
                  })}
                </ul>
              </ProjectScrollPanel>
            )}
          </Card>
        ) : null}
      </div>

      <Modal
        open={generateModal}
        onClose={() => setGenerateModal(false)}
        title={t("reports.generateModal")}
        description={t("reports.description")}
        size="md"
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setGenerateModal(false)}>
              {t("common.cancel")}
            </Button>
            <Button onClick={() => void handleGenerate()} loading={generating}>
              {t("reports.generatePdf")}
            </Button>
          </div>
        }
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <Select
            label={t("common.format")}
            value={reportType}
            onChange={(e) => setReportType(e.target.value as ReportType)}
          >
            {reportTypes.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </Select>
          <Select
            label={t("common.language")}
            value={language}
            onChange={(e) => setLanguage(e.target.value as "pt" | "en")}
          >
            <option value="pt">{t("reports.languages.pt")}</option>
            <option value="en">{t("reports.languages.en")}</option>
          </Select>
          <Select
            label={t("common.currency")}
            value={reportCurrency}
            onChange={(e) => setReportCurrency(e.target.value as "AOA" | "USD" | "EUR")}
            className="sm:col-span-2"
          >
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
            <option value="AOA">AOA</option>
          </Select>
        </div>
      </Modal>

      <SendReportEmailModal
        open={emailModalOpen}
        onClose={() => {
          setEmailModalOpen(false);
          setSelectedReport(null);
        }}
        project={project}
        report={selectedReport}
        onSent={() => void loadEmailHistory()}
      />

      <Modal
        open={actionModal === "whatsapp"}
        onClose={() => setActionModal(null)}
        title={t("reports.shareWhatsApp")}
        description={t("reports.shareLinkHint")}
        size="sm"
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setActionModal(null)}>
              {t("common.cancel")}
            </Button>
            <Button onClick={() => void handleShareWhatsApp()} loading={submitting}>
              {t("reports.generateLink")}
            </Button>
          </div>
        }
      >
        <Input
          label={t("reports.phoneOptional")}
          value={whatsappPhone}
          onChange={(e) => setWhatsappPhone(e.target.value)}
          placeholder="+244 9XX XXX XXX"
        />
      </Modal>

      <Modal
        open={actionModal === "bank"}
        onClose={() => setActionModal(null)}
        title={t("reports.submitBankTitle")}
        description={t("reports.bankHint")}
        size="sm"
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setActionModal(null)}>
              {t("common.cancel")}
            </Button>
            <Button onClick={() => void handleSubmitBank()} loading={submitting}>
              {t("reports.submit")}
            </Button>
          </div>
        }
      >
        <Select
          label={t("reports.bank")}
          value={bankCode}
          onChange={(e) => setBankCode(e.target.value as "bfa" | "bda")}
        >
          <option value="bfa">BFA</option>
          <option value="bda">BDA</option>
        </Select>
      </Modal>
    </div>
  );
}
