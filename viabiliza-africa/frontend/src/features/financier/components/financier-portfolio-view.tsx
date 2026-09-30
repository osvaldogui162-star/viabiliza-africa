"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { Activity, ArrowRight, Building2, Landmark, Sparkles } from "lucide-react";
import { useAuth } from "@/components/providers/auth-provider";
import { useI18n } from "@/components/providers/locale-provider";
import { BankLogoBadge } from "@/features/financier/components/bank-logo-badge";
import { FinancierStatusPill } from "@/features/financier/components/financier-status-pill";
import { PageLoader } from "@/components/ui/spinner";
import { financierApi } from "@/lib/api/financier-api";
import { ApiError } from "@/lib/api/http-client";
import type { FinancierPortfolioResponse, FinancingListItem } from "@/lib/types/financier";

function PortfolioCard({ item, statusLabel }: { item: FinancingListItem; statusLabel: string }) {
  const { formatMoney } = useI18n();
  return (
    <Link
      href={`/financiador/${item.id}`}
      className="group relative overflow-hidden rounded-2xl border border-zinc-200/80 bg-white p-5 shadow-sm transition hover:-translate-y-1 hover:border-teal-200 hover:shadow-xl"
    >
      <div className="absolute -right-8 -top-8 h-32 w-32 rounded-full bg-gradient-to-br from-teal-100/80 to-transparent opacity-60" />
      <div className="relative flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-3">
            <BankLogoBadge bank={item.bank} size="md" />
            <div className="min-w-0">
              <h3 className="truncate font-[family-name:var(--font-poppins)] text-lg font-bold text-[var(--brand-navy)]">
                {item.project_name}
              </h3>
              <p className="truncate text-sm text-zinc-500">{item.company_name ?? "—"}</p>
            </div>
          </div>
        </div>
        <FinancierStatusPill status={item.monitoring_status} label={statusLabel} />
      </div>

      <div className="relative mt-5 grid grid-cols-2 gap-3">
        <div className="rounded-xl bg-zinc-50 px-3 py-2">
          <p className="text-[10px] font-semibold uppercase text-zinc-500">Aprovado</p>
          <p className="text-sm font-bold tabular-nums text-[var(--brand-navy)]">
            {formatMoney(parseFloat(item.approved_amount), item.currency)}
          </p>
        </div>
        <div className="rounded-xl bg-teal-50/80 px-3 py-2">
          <p className="text-[10px] font-semibold uppercase text-teal-800/70">Utilização</p>
          <p className="text-sm font-bold tabular-nums text-teal-900">
            {item.utilization_pct != null ? `${item.utilization_pct}%` : "—"}
          </p>
        </div>
      </div>

      <p className="relative mt-4 flex items-center gap-1 text-sm font-semibold text-[#00777f] opacity-0 transition group-hover:opacity-100">
        Ver execução em gráficos
        <ArrowRight className="h-4 w-4" />
      </p>
    </Link>
  );
}

export function FinancierPortfolioView() {
  const { user } = useAuth();
  const { t, formatMoney } = useI18n();
  const [data, setData] = useState<FinancierPortfolioResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await financierApi.portfolio());
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

  const statusLabel = (s: FinancingListItem["monitoring_status"]) => {
    if (s === "on_track") return t("financier.statusOnTrack");
    if (s === "attention") return t("financier.statusAttention");
    return t("financier.statusCritical");
  };

  const viewerBank = data?.viewer_bank;

  return (
    <div className="min-h-[calc(100vh-3.5rem)] bg-[var(--background)]">
      {user?.role !== "bank" ? (
      <header className="relative overflow-hidden border-b border-zinc-100 bg-[var(--brand-navy)] px-4 py-10 text-white sm:px-8">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(0,119,127,0.35),transparent_45%),radial-gradient(circle_at_80%_0%,rgba(45,212,191,0.2),transparent_40%)]" />
        <div className="relative mx-auto flex max-w-6xl flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="flex items-center gap-2 text-sm font-medium text-teal-200/90">
              <Landmark className="h-4 w-4" />
              {t("financier.portalTag")}
            </p>
            <h1 className="mt-2 font-[family-name:var(--font-poppins)] text-3xl font-bold tracking-tight sm:text-4xl">
              {t("financier.title")}
            </h1>
            <p className="mt-2 max-w-xl text-sm text-zinc-300">{t("financier.subtitle")}</p>
          </div>
          {viewerBank ? (
            <div className="flex items-center gap-4 rounded-2xl border border-white/10 bg-white/5 px-5 py-4 backdrop-blur-sm">
              <BankLogoBadge bank={viewerBank} size="lg" />
              <div>
                <p className="text-xs uppercase tracking-wide text-teal-200/80">{t("financier.institution")}</p>
                <p className="text-sm font-semibold">{viewerBank.label_pt}</p>
              </div>
            </div>
          ) : user?.role === "financial" ? (
            <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm">
              <Building2 className="h-5 w-5 text-teal-300" />
              {t("financier.analystPortfolioHint")}
            </div>
          ) : null}
        </div>
      </header>
      ) : null}

      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
        {data ? (
          <div className="mb-8 grid gap-3 sm:grid-cols-4">
            {[
              {
                label: t("financier.statExposure"),
                value: formatMoney(parseFloat(data.stats.total_exposure || "0"), "AOA"),
                icon: Activity,
              },
              { label: t("financier.statusOnTrack"), value: String(data.stats.on_track), icon: Sparkles },
              { label: t("financier.statusAttention"), value: String(data.stats.attention), icon: Activity },
              { label: t("financier.statusCritical"), value: String(data.stats.critical), icon: Activity },
            ].map((stat) => (
              <div
                key={stat.label}
                className="rounded-2xl border border-zinc-100 bg-white px-4 py-3 shadow-sm"
              >
                <p className="text-[11px] font-semibold uppercase tracking-wide text-zinc-500">{stat.label}</p>
                <p className="mt-1 text-2xl font-bold tabular-nums text-[var(--brand-navy)]">{stat.value}</p>
              </div>
            ))}
          </div>
        ) : null}

        {loading ? <PageLoader message={t("common.loading")} layout="section" /> : null}

        {error ? (
          <p className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{error}</p>
        ) : null}

        {!loading && data && data.items.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-zinc-200 bg-white px-6 py-16 text-center">
            <p className="text-lg font-semibold text-zinc-800">{t("financier.emptyTitle")}</p>
            <p className="mt-2 text-sm text-zinc-500">{t("financier.emptyBody")}</p>
          </div>
        ) : null}

        <div className="grid gap-4 md:grid-cols-2">
          {data?.items.map((item) => (
            <PortfolioCard key={item.id} item={item} statusLabel={statusLabel(item.monitoring_status)} />
          ))}
        </div>
      </main>
    </div>
  );
}
