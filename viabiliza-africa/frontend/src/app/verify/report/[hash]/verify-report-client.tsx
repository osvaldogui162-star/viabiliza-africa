"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, FileText, ShieldAlert, ShieldCheck } from "lucide-react";

import { PageLoader } from "@/components/ui/spinner";
import { LocaleSelector } from "@/components/layout/locale-selector";
import { useI18n } from "@/components/providers/locale-provider";
import { verifyReportPublic } from "@/lib/api/ingestion-api";
import { formatDateTime } from "@/lib/utils/format";
import type { ReportVerification } from "@/lib/types/ingestion";

export function VerifyReportClient({ hash }: { hash: string }) {
  const { t, intlLocale } = useI18n();
  const [data, setData] = useState<ReportVerification | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void verifyReportPublic(hash)
      .then(setData)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [hash]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-sky-50 to-white">
      <div className="mx-auto max-w-3xl px-4 py-10">
        <div className="mb-4 flex justify-end">
          <LocaleSelector />
        </div>
        <header className="mb-8 text-center">
          <p className="text-sm font-medium uppercase tracking-wider text-sky-700">
            ViabilizA+ África
          </p>
          <h1 className="mt-2 text-3xl font-bold text-zinc-900">{t("verify.reportTitle")}</h1>
          <p className="mt-2 text-sm text-zinc-600">{t("verify.reportSubtitle")}</p>
        </header>

        {loading ? (
          <PageLoader message={t("verify.verifying")} layout="section" />
        ) : error ? (
          <div className="rounded-2xl border border-red-200 bg-red-50 p-8 text-center">
            <ShieldAlert className="mx-auto h-10 w-10 text-red-600" />
            <p className="mt-3 font-semibold text-red-900">{t("verify.notVerified")}</p>
            <p className="mt-1 text-sm text-red-700">{error}</p>
          </div>
        ) : data ? (
          <div className="space-y-6">
            <div className="rounded-2xl border border-emerald-200 bg-emerald-50/80 p-6">
              <div className="flex items-start gap-4">
                <ShieldCheck className="h-10 w-10 shrink-0 text-emerald-600" />
                <div>
                  <p className="text-lg font-semibold text-zinc-900">
                    {data.message ?? t("verify.reportAuthentic")}
                  </p>
                  <p className="mt-1 text-sm text-zinc-600">{data.title}</p>
                  <div className="mt-3 flex flex-wrap gap-2 text-sm text-zinc-700">
                    <span className="rounded-full bg-white px-3 py-1">{data.report_type_label}</span>
                    <span className="rounded-full bg-white px-3 py-1">
                      {data.language.toUpperCase()} · {data.currency}
                    </span>
                  </div>
                  <p className="mt-3 font-mono text-xs text-zinc-500 break-all">
                    Hash SHA-256: {data.verification_hash}
                  </p>
                  <p className="mt-2 flex items-center gap-1 text-sm text-emerald-800">
                    <CheckCircle2 className="h-4 w-4" />
                    {t("verify.generatedAt", {
                      date: formatDateTime(data.created_at, intlLocale),
                    })}
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border bg-white p-6 shadow-sm">
              <div className="flex items-center gap-3">
                <FileText className="h-8 w-8 text-sky-600" />
                <div>
                  <p className="font-medium">{t("verify.verifiedDocument")}</p>
                  <p className="text-sm text-zinc-500">
                    {data.file_size_bytes
                      ? `${Math.round(data.file_size_bytes / 1024)} KB`
                      : t("verify.sizeUnavailable")}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
