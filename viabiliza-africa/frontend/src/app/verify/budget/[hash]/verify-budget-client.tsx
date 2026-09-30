"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, ShieldAlert, ShieldCheck } from "lucide-react";

import { PageLoader } from "@/components/ui/spinner";
import { LocaleSelector } from "@/components/layout/locale-selector";
import { useI18n } from "@/components/providers/locale-provider";
import { verifyBudgetPublic } from "@/lib/api/ingestion-api";
import { formatCurrencyAmount, formatDateTime } from "@/lib/utils/format";
import type { BudgetVerification } from "@/lib/types/ingestion";

export function VerifyBudgetClient({ hash }: { hash: string }) {
  const { t, locale, intlLocale } = useI18n();
  const [data, setData] = useState<BudgetVerification | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const statusLabel: Record<string, string> =
    locale === "en"
      ? { draft: "Draft", approved: "Approved", superseded: "Superseded" }
      : { draft: "Rascunho", approved: "Aprovado", superseded: "Substituído" };

  const sourceLabel: Record<string, string> =
    locale === "en"
      ? {
          manual: "Manual",
          excel: "Excel",
          scraping: "Scraping",
          agt: "AGT",
          unknown: "Unknown",
        }
      : {
          manual: "Manual",
          excel: "Excel",
          scraping: "Scraping",
          agt: "AGT",
          unknown: "Desconhecida",
        };

  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), 20000);

    void verifyBudgetPublic(hash, controller.signal)
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch((err: Error) => {
        if (cancelled) return;
        if (err.name === "AbortError") {
          setError(
            locale === "en"
              ? "Verification timed out. Use the PC's current LAN IP (e.g. 192.168.1.185), not an old IP."
              : "A verificação demorou demasiado. Use o IP actual do PC na rede (ex.: 192.168.1.185), não um IP antigo.",
          );
        } else {
          setError(err.message);
        }
      })
      .finally(() => {
        window.clearTimeout(timer);
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
      controller.abort();
      window.clearTimeout(timer);
    };
  }, [hash, locale]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-emerald-50 to-white">
      <div className="mx-auto max-w-4xl px-4 py-10">
        <div className="mb-4 flex justify-end">
          <LocaleSelector />
        </div>
        <header className="mb-8 text-center">
          <p className="text-sm font-medium uppercase tracking-wider text-emerald-700">
            ViabilizA+ África
          </p>
          <h1 className="mt-2 text-3xl font-bold text-zinc-900">{t("verify.budgetTitle")}</h1>
          <p className="mt-2 text-sm text-zinc-600">{t("verify.budgetSubtitle")}</p>
        </header>

        {loading ? (
          <PageLoader
            message={locale === "en" ? "Verifying budget…" : "A verificar orçamento…"}
            layout="section"
          />
        ) : error ? (
          <div className="rounded-2xl border border-red-200 bg-red-50 p-8 text-center">
            <ShieldAlert className="mx-auto h-10 w-10 text-red-600" />
            <p className="mt-3 font-semibold text-red-900">
              {locale === "en" ? "Budget not verified" : "Orçamento não verificado"}
            </p>
            <p className="mt-1 text-sm text-red-700">{error}</p>
          </div>
        ) : data ? (
          <div className="space-y-6">
            <div
              className={`rounded-2xl border p-6 ${
                data.status === "approved"
                  ? "border-emerald-200 bg-emerald-50/80"
                  : "border-amber-200 bg-amber-50/80"
              }`}
            >
              <div className="flex items-start gap-4">
                {data.valid ? (
                  <ShieldCheck className="h-10 w-10 shrink-0 text-emerald-600" />
                ) : (
                  <ShieldAlert className="h-10 w-10 shrink-0 text-amber-600" />
                )}
                <div>
                  <p className="text-lg font-semibold text-zinc-900">
                    {data.valid
                      ? locale === "en"
                        ? "Authentic budget"
                        : "Orçamento autêntico"
                      : locale === "en"
                        ? "Budget found"
                        : "Orçamento encontrado"}
                  </p>
                  {data.project_name ? (
                    <p className="mt-1 text-sm font-medium text-zinc-800">{data.project_name}</p>
                  ) : null}
                  {data.company_name ? (
                    <p className="text-sm text-zinc-600">{data.company_name}</p>
                  ) : null}
                  <p className="mt-1 text-sm text-zinc-600">
                    {data.budget_number} · {data.title} ·{" "}
                    {statusLabel[data.status] ?? data.status}
                  </p>
                  <p className="mt-2 text-2xl font-bold text-emerald-800">
                    {formatCurrencyAmount(data.total_amount, data.currency, intlLocale)}
                  </p>
                  <p className="mt-2 font-mono text-xs text-zinc-500 break-all">
                    Hash SHA-256: {data.verification_hash}
                  </p>
                  {data.approved_at ? (
                    <p className="mt-2 flex items-center gap-1 text-sm text-emerald-800">
                      <CheckCircle2 className="h-4 w-4" />
                      {locale === "en" ? "Approved on" : "Aprovado em"}{" "}
                      {formatDateTime(data.approved_at, intlLocale)}
                    </p>
                  ) : null}
                  <p className="mt-1 text-xs text-zinc-500">
                    {t("verify.generatedAt", {
                      date: formatDateTime(data.generated_at ?? data.created_at, intlLocale),
                    })}
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold">
                {locale === "en"
                  ? `Traceable items (${data.items_count})`
                  : `Itens rastreáveis (${data.items_count})`}
              </h2>
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead className="bg-zinc-50 text-left">
                    <tr>
                      <th className="p-2">{locale === "en" ? "Type" : "Tipo"}</th>
                      <th className="p-2">{locale === "en" ? "Description" : "Descrição"}</th>
                      <th className="p-2">{locale === "en" ? "Source" : "Fonte"}</th>
                      <th className="p-2">Total</th>
                      <th className="p-2">Hash</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.items.map((item, index) => (
                      <tr key={`${item.item_hash}-${index}`} className="border-t">
                        <td className="p-2 uppercase">{item.item_type}</td>
                        <td className="p-2">
                          <p className="font-medium">{item.description}</p>
                          <p className="text-xs text-zinc-500">{item.category}</p>
                        </td>
                        <td className="p-2 text-xs text-zinc-600">
                          {item.source_label ??
                            sourceLabel[item.source ?? "unknown"] ??
                            item.source ??
                            "—"}
                        </td>
                        <td className="p-2 whitespace-nowrap">
                          {formatCurrencyAmount(item.total_amount, data.currency, intlLocale)}
                        </td>
                        <td className="p-2 font-mono text-xs text-zinc-500">
                          {item.item_hash.slice(0, 12)}…
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <p className="text-center text-xs text-zinc-500">
              {locale === "en"
                ? "Real-time verification · Data registered with SHA-256 hash per item"
                : "Verificação em tempo real · Dados registados com hash SHA-256 por item"}
            </p>
          </div>
        ) : null}
      </div>
    </div>
  );
}
