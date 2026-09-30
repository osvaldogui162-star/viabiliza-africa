"use client";

import { CheckCircle2, Circle, PlugZap } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { useI18n } from "@/components/providers/locale-provider";
import { BankPortalCanvas } from "@/features/financier/components/bank-portal-canvas";
import { PageLoader } from "@/components/ui/spinner";
import { financierApi } from "@/lib/api/financier-api";
import { ApiError } from "@/lib/api/http-client";
import type { FinancierBillingIntegrationItem } from "@/lib/types/financier";
import { cn } from "@/lib/utils/cn";

export function TerminalBillingIntegrationsView() {
  const { t } = useI18n();
  const [items, setItems] = useState<FinancierBillingIntegrationItem[]>([]);
  const [connected, setConnected] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await financierApi.billingIntegrations();
      setItems(res.items);
      setConnected(res.connected_count);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : t("common.error"));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <BankPortalCanvas>
      <header className="bank-dash-card bank-dash-rise mb-6 p-5">
        <p className="flex items-center gap-2 text-sm font-medium text-[var(--brand-teal)]">
          <PlugZap className="h-4 w-4" />
          {t("terminal.navIntegration")}
        </p>
        <h1 className="bank-dash-card-title mt-2 text-2xl">{t("terminal.integrationTitle")}</h1>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-[var(--muted)]">
          {t("terminal.integrationSubtitle")}
        </p>
        {!loading ? (
          <p className="mt-3 text-sm font-semibold text-[var(--brand-navy)]">
            {connected} / {items.length} {t("terminal.connectedProjects")}
          </p>
        ) : null}
      </header>

      {loading ? <PageLoader message={t("common.loading")} layout="section" /> : null}
      {error ? <p className="text-sm text-rose-700">{error}</p> : null}

      <div className="space-y-4">
        {items.map((row) => {
          const status = row.integration?.connection_status ?? "disconnected";
          const active = status === "active";
          return (
            <article key={row.financing_id} className="bank-portal-panel rounded-2xl p-5">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h2 className="font-semibold text-[var(--brand-navy)]">{row.project_name}</h2>
                  <p className="text-xs text-[var(--muted)]">{row.company_name ?? "—"}</p>
                  {row.integration?.erp_label ? (
                    <p className="mt-1 text-xs text-[var(--muted)]">
                      ERP: {row.integration.erp_label}
                      {row.integration.last_hash ? ` · SHA-256 …${row.integration.last_hash.slice(-8)}` : ""}
                    </p>
                  ) : null}
                </div>
                <span
                  className={cn(
                    "rounded-full px-3 py-1 text-xs font-bold",
                    active ? "bg-emerald-100 text-emerald-800" : "bg-rose-100 text-rose-900",
                  )}
                >
                  {active ? t("terminal.billingConnected") : t("terminal.billingDisconnected")}
                </span>
              </div>
              <ol className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-5">
                {row.steps.map((step) => (
                  <li
                    key={step.code}
                    className={cn(
                      "flex items-start gap-2 rounded-xl border px-3 py-2 text-xs",
                      step.done ? "border-emerald-200 bg-emerald-50/50" : "border-[var(--border)] bg-white",
                    )}
                  >
                    {step.done ? (
                      <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />
                    ) : (
                      <Circle className="mt-0.5 h-4 w-4 shrink-0 text-[var(--muted)]" />
                    )}
                    <span>
                      <span className="font-bold text-[var(--brand-navy)]">{step.step}.</span> {step.label_pt}
                    </span>
                  </li>
                ))}
              </ol>
            </article>
          );
        })}
        {!loading && items.length === 0 ? (
          <p className="text-sm text-[var(--muted)]">{t("bankPortal.portfolioEmptyHint")}</p>
        ) : null}
      </div>
    </BankPortalCanvas>
  );
}
