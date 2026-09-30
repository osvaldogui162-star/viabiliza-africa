"use client";

import { useMemo, useState } from "react";
import {
  CheckCircle2,
  FileText,
  Hash,
  Mail,
  Paperclip,
  Send,
  ShieldCheck,
} from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { Textarea } from "@/components/ui/textarea";
import { useI18n } from "@/components/providers/locale-provider";
import { ApiError } from "@/lib/api/http-client";
import { reportsApi } from "@/lib/api/reports-api";
import { formatDateTime } from "@/lib/utils/format";
import type { Report } from "@/lib/types/reports";
import type { Project } from "@/lib/types/project";

function formatBytes(bytes: number | null | undefined) {
  if (!bytes || bytes <= 0) return "—";
  if (bytes < 1024) return `${bytes} B`;
  return `${(bytes / 1024).toFixed(1)} KB`;
}

function isValidEmail(value: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
}

export function SendReportEmailModal({
  open,
  onClose,
  project,
  report,
  onSent,
}: {
  open: boolean;
  onClose: () => void;
  project: Project;
  report: Report | null;
  onSent?: () => void;
}) {
  const { t, locale, intlLocale } = useI18n();

  const defaultSubject = useMemo(() => {
    if (!report) return "";
    const title = report.title || report.report_type_label;
    return `ViabilizA+ África — ${title}`;
  }, [report]);

  const [toEmail, setToEmail] = useState("");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [sentReceipt, setSentReceipt] = useState<{
    to: string;
    subject: string;
    sent_at: string;
    verification_hash?: string;
  } | null>(null);

  const emailError =
    toEmail.trim().length > 0 && !isValidEmail(toEmail)
      ? t("email.invalidEmail")
      : undefined;
  const subjectError =
    subject.trim().length > 0 && subject.trim().length < 3
      ? t("email.subjectShort")
      : undefined;

  function resetForm(nextReport: Report | null) {
    setToEmail("");
    setSubject(
      nextReport
        ? `ViabilizA+ África — ${nextReport.title || nextReport.report_type_label}`
        : "",
    );
    const title = nextReport?.title || nextReport?.report_type_label || "";
    setMessage(
      nextReport
        ? t("email.defaultBody", { title, project: project.name })
        : "",
    );
    setSentReceipt(null);
  }

  if (open && report && subject === "" && !sentReceipt) {
    resetForm(report);
  }

  async function handleSend() {
    if (!report) return;
    if (!isValidEmail(toEmail)) {
      toast.error(t("email.invalidTo"));
      return;
    }
    const resolvedSubject = subject.trim() || defaultSubject;
    if (resolvedSubject.length < 3) {
      toast.error(t("email.subjectRequired"));
      return;
    }

    setSubmitting(true);
    try {
      const result = await reportsApi.sendEmail(project.id, report.id, {
        to_email: toEmail.trim(),
        subject: resolvedSubject,
        message: message.trim() || undefined,
      });
      setSentReceipt({
        to: result.to,
        subject: result.subject ?? resolvedSubject,
        sent_at: result.sent_at ?? new Date().toISOString(),
        verification_hash: result.verification_hash,
      });
      toast.success(t("email.sendSuccess"));
      onSent?.();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("email.sendError"));
    } finally {
      setSubmitting(false);
    }
  }

  function handleClose() {
    resetForm(null);
    onClose();
  }

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title={t("email.title")}
      size="lg"
      className="max-w-2xl"
    >
      <div className="space-y-5">
        <div className="overflow-hidden rounded-xl border border-teal-100 bg-gradient-to-br from-teal-50 via-white to-emerald-50/50 p-4">
          <div className="flex items-start gap-3">
            <div className="rounded-xl border border-teal-100 bg-white p-3 text-teal-700 shadow-sm">
              <Mail className="h-5 w-5" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-[10px] font-semibold uppercase tracking-wider text-teal-700">
                {locale === "en" ? "Email service · PDF attached" : "Serviço de e-mail · PDF em anexo"}
              </p>
              <p className="mt-1 truncate text-base font-semibold text-zinc-900">
                {report?.title || report?.report_type_label || t("common.report")}
              </p>
              <p className="mt-0.5 text-sm text-zinc-600">
                {project.name} · {report?.language?.toUpperCase()} · {report?.currency}
              </p>
            </div>
          </div>
        </div>

        {sentReceipt ? (
            <div className="space-y-4 rounded-2xl border border-emerald-200 bg-emerald-50/70 p-5">
              <div className="flex items-center gap-2 text-emerald-800">
                <CheckCircle2 className="h-5 w-5" />
                <p className="font-semibold">{t("email.sentTitle")}</p>
              </div>
              <p className="text-sm text-zinc-600">{t("email.sentDesc")}</p>
              <dl className="grid gap-3 text-sm sm:grid-cols-2">
                <div>
                  <dt className="text-xs uppercase text-zinc-500">{t("email.recipient")}</dt>
                  <dd className="font-medium text-zinc-900">{sentReceipt.to}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase text-zinc-500">{t("common.date")}</dt>
                  <dd className="font-medium text-zinc-900">
                    {formatDateTime(sentReceipt.sent_at, intlLocale)}
                  </dd>
                </div>
                <div className="sm:col-span-2">
                  <dt className="text-xs uppercase text-zinc-500">{t("email.subject")}</dt>
                  <dd className="font-medium text-zinc-900">{sentReceipt.subject}</dd>
                </div>
                {sentReceipt.verification_hash ? (
                  <div className="sm:col-span-2">
                    <dt className="mb-1 flex items-center gap-1 text-xs uppercase text-zinc-500">
                      <Hash className="h-3 w-3" /> Hash SHA-256
                    </dt>
                    <dd className="break-all font-mono text-xs text-zinc-600">
                      {sentReceipt.verification_hash}
                    </dd>
                  </div>
                ) : null}
              </dl>
              <div className="flex flex-wrap gap-2">
                <Button
                  variant="outline"
                  onClick={() => {
                    setSentReceipt(null);
                    if (report) resetForm(report);
                  }}
                >
                  {locale === "en" ? "Send another" : "Enviar outro"}
                </Button>
                <Button onClick={handleClose}>{t("common.close")}</Button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="sm:col-span-2">
                  <Input
                    label={t("email.recipient")}
                    type="email"
                    value={toEmail}
                    onChange={(e) => setToEmail(e.target.value)}
                    placeholder="recipient@company.com"
                    error={emailError}
                    autoFocus
                  />
                </div>
                <div className="sm:col-span-2">
                  <Input
                    label={t("email.subject")}
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    placeholder={defaultSubject}
                    error={subjectError}
                  />
                </div>
                <div className="sm:col-span-2">
                  <Textarea
                    label={t("email.message")}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    rows={4}
                    placeholder={t("email.messagePlaceholder")}
                  />
                </div>
              </div>

              <div className="rounded-xl border border-dashed border-zinc-200 bg-zinc-50/80 p-4">
                <div className="flex items-start gap-3">
                  <Paperclip className="mt-0.5 h-5 w-5 text-zinc-500" />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-zinc-800">{t("email.attachment")}</p>
                    <p className="mt-1 flex items-center gap-2 text-sm text-zinc-600">
                      <FileText className="h-4 w-4 text-emerald-600" />
                      <span className="truncate">
                        relatorio_{report?.report_type ?? "pdf"}.pdf
                      </span>
                      <span className="text-zinc-400">·</span>
                      <span>{formatBytes(report?.file_size_bytes)}</span>
                    </p>
                    {(report?.verification_hash || report?.hash) && (
                      <p className="mt-2 flex items-start gap-1.5 font-mono text-[11px] text-zinc-500">
                        <ShieldCheck className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-600" />
                        <span className="break-all">
                          {report.verification_hash || report.hash}
                        </span>
                      </p>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap justify-end gap-2 border-t pt-4">
                <Button variant="outline" onClick={handleClose} disabled={submitting}>
                  {t("common.cancel")}
                </Button>
                <Button onClick={() => void handleSend()} loading={submitting}>
                  <Send className="h-4 w-4" /> {t("reports.sendEmail")}
                </Button>
              </div>
            </div>
          )}
      </div>
    </Modal>
  );
}
