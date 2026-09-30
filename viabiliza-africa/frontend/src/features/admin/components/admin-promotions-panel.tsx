"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  ExternalLink,
  Megaphone,
  RefreshCw,
  Sparkles,
  ToggleLeft,
  ToggleRight,
} from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { PageLoader } from "@/components/ui/spinner";
import { useI18n } from "@/components/providers/locale-provider";
import { adminApi } from "@/lib/api/admin-api";
import { ApiError } from "@/lib/api/http-client";
import { formatAoa } from "@/lib/pricing/plan-price";
import type { AdminPromotionOverview } from "@/lib/types/admin";
import { cn } from "@/lib/utils/cn";

const DURATIONS = [3, 4, 5, 6] as const;

export function AdminPromotionsPanel() {
  const { locale } = useI18n();
  const en = locale === "en";
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [overview, setOverview] = useState<AdminPromotionOverview | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await adminApi.getPricingPromotionOverview();
      setOverview(data);
    } catch (error) {
      toast.error(
        error instanceof ApiError
          ? error.message
          : en
            ? "Failed to load promotions"
            : "Erro ao carregar promoções",
      );
      setOverview(null);
    } finally {
      setLoading(false);
    }
  }, [en]);

  useEffect(() => {
    void load();
  }, [load]);

  async function activate(months: (typeof DURATIONS)[number]) {
    setActionLoading(true);
    try {
      const data = await adminApi.activatePricingPromotion(months);
      setOverview(data);
      toast.success(
        en ? `Campaign active for ${months} months` : `Campanha activa por ${months} meses`,
      );
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Activation failed" : "Falha ao activar");
    } finally {
      setActionLoading(false);
    }
  }

  async function deactivate() {
    if (!confirm(en ? "End the commercial campaign?" : "Terminar a campanha comercial?")) return;
    setActionLoading(true);
    try {
      const data = await adminApi.deactivatePricingPromotion();
      setOverview(data);
      toast.success(en ? "Campaign ended" : "Campanha terminada");
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Failed" : "Falha");
    } finally {
      setActionLoading(false);
    }
  }

  if (loading) {
    return <PageLoader message={en ? "Loading promotions..." : "A carregar promoções..."} />;
  }

  if (!overview) {
    return (
      <Card className="p-8 text-center">
        <p className="text-sm text-zinc-600">
          {en
            ? "Could not load promotion data. Check backend and migration 025."
            : "Não foi possível carregar promoções. Verifique o backend e a migration 025."}
        </p>
        <Button className="mt-4" onClick={() => void load()}>
          {en ? "Retry" : "Tentar novamente"}
        </Button>
      </Card>
    );
  }

  const { promotion, pricing_rules, matrix } = overview;
  const active = promotion.active;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-[#00777f]">
            {en ? "Commercial" : "Comercial"}
          </p>
          <h2 className="mt-1 flex items-center gap-2 text-xl font-bold text-[#011636]">
            <Megaphone className="h-6 w-6 text-[#ffa900]" />
            {en ? "Pricing campaigns" : "Campanhas de preços"}
          </h2>
          <p className="mt-1 max-w-2xl text-sm text-zinc-500">
            {en ? pricing_rules.description_en : pricing_rules.description_pt}
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/planos" target="_blank">
            <Button variant="outline" size="sm">
              <ExternalLink className="h-4 w-4" />
              {en ? "Public /planos" : "Ver /planos"}
            </Button>
          </Link>
          <Button variant="outline" size="sm" onClick={() => void load()} disabled={actionLoading}>
            <RefreshCw className={cn("h-4 w-4", actionLoading && "animate-spin")} />
            {en ? "Refresh" : "Actualizar"}
          </Button>
        </div>
      </div>

      <Card
        className={cn(
          "overflow-hidden border-2 p-0",
          active ? "border-[#ffa900]/50" : "border-zinc-200",
        )}
      >
        <div
          className={cn(
            "px-6 py-5",
            active
              ? "bg-gradient-to-r from-[#fff8eb] via-white to-[#eef8f9]"
              : "bg-zinc-50",
          )}
        >
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              {active ? (
                <ToggleRight className="h-10 w-10 text-[#00777f]" aria-hidden />
              ) : (
                <ToggleLeft className="h-10 w-10 text-zinc-400" aria-hidden />
              )}
              <div>
                <p className="text-lg font-bold text-[#011636]">
                  {active
                    ? en
                      ? "Campaign active"
                      : "Campanha activa"
                    : en
                      ? "Campaign inactive"
                      : "Campanha inactiva"}
                </p>
                <p className="text-sm text-zinc-600">
                  {active ? (
                    <>
                      −{promotion.discount_pct ?? 20}% ·{" "}
                      {promotion.duration_months
                        ? en
                          ? `${promotion.duration_months} months`
                          : `${promotion.duration_months} meses`
                        : null}
                      {promotion.ends_at ? (
                        <>
                          {" "}
                          · {en ? "Until" : "Até"}{" "}
                          {new Date(promotion.ends_at).toLocaleString(en ? "en-GB" : "pt-AO")}
                        </>
                      ) : null}
                    </>
                  ) : en ? (
                    "Fixed catalog prices on checkout and /planos"
                  ) : (
                    "Preços fixos do catálogo no checkout e em /planos"
                  )}
                </p>
              </div>
            </div>
            {active ? (
              <span className="inline-flex items-center gap-1 rounded-full bg-[#ffa900]/15 px-3 py-1 text-xs font-bold text-[#92400e]">
                <Sparkles className="h-3.5 w-3.5" />
                LIVE
              </span>
            ) : null}
          </div>

          <div className="mt-6 flex flex-wrap gap-2">
            {DURATIONS.map((m) => (
              <Button
                key={m}
                size="sm"
                disabled={actionLoading || active}
                onClick={() => void activate(m)}
                className="bg-[#011636] hover:bg-[#023048]"
              >
                {en ? `Activate ${m} months` : `Activar ${m} meses`}
              </Button>
            ))}
            <Button
              size="sm"
              variant="danger"
              disabled={actionLoading || !active}
              onClick={() => void deactivate()}
            >
              {en ? "End campaign" : "Terminar campanha"}
            </Button>
          </div>
        </div>
      </Card>

      <Card className="overflow-hidden p-0">
        <div className="border-b border-zinc-100 bg-white px-5 py-4">
          <h3 className="font-semibold text-zinc-900">
            {en ? "Price matrix (AOA, before VAT display)" : "Matriz de preços (AOA, subtotal checkout)"}
          </h3>
          <p className="text-xs text-zinc-500">
            {en
              ? "Reference = legacy price · Promo = −20% on reference · Fixed = current catalog"
              : "Referência = preço anterior · Promo = −20% sobre referência · Fixo = catálogo actual"}
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[880px] text-sm">
            <thead>
              <tr className="bg-[#011636] text-left text-xs uppercase tracking-wide text-white">
                <th className="px-4 py-3">{en ? "Plan" : "Plano"}</th>
                <th className="px-4 py-3">{en ? "Period" : "Período"}</th>
                <th className="px-4 py-3 text-right">{en ? "Reference" : "Referência"}</th>
                <th className="px-4 py-3 text-right">{en ? "Fixed" : "Fixo"}</th>
                <th className="px-4 py-3 text-right">{en ? "Promo (−20%)" : "Promo (−20%)"}</th>
                <th className="px-4 py-3 text-right">{en ? "Checkout now" : "Checkout actual"}</th>
              </tr>
            </thead>
            <tbody>
              {matrix.map((row, i) => (
                <tr key={`${row.plan_code}-${row.billing_period}`} className={i % 2 === 0 ? "bg-white" : "bg-zinc-50"}>
                  <td className="border-t border-zinc-100 px-4 py-2.5 font-medium text-zinc-800">
                    {row.plan_name}
                  </td>
                  <td className="border-t border-zinc-100 px-4 py-2.5 text-zinc-600">
                    {en ? row.billing_period : row.billing_period_label_pt}
                  </td>
                  <td className="border-t border-zinc-100 px-4 py-2.5 text-right text-zinc-500 line-through">
                    {formatAoa(row.reference_aoa)}
                  </td>
                  <td className="border-t border-zinc-100 px-4 py-2.5 text-right text-zinc-700">
                    {formatAoa(row.fixed_aoa)}
                  </td>
                  <td className="border-t border-zinc-100 px-4 py-2.5 text-right font-medium text-[#00777f]">
                    {formatAoa(row.promotional_aoa)}
                  </td>
                  <td className="border-t border-zinc-100 px-4 py-2.5 text-right">
                    <span
                      className={cn(
                        "font-bold",
                        row.promotion_applied ? "text-[#ffa900]" : "text-[#011636]",
                      )}
                    >
                      {formatAoa(row.checkout_subtotal_aoa)}
                    </span>
                    <span className="ml-1 text-xs text-zinc-400">
                      (+ IVA → {formatAoa(row.checkout_total_aoa)})
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <p className="text-xs text-zinc-500">
        {en
          ? "Tip: sync plans under the Plans tab after changing the catalog. Migration 025 creates platform_settings."
          : "Dica: sincronize os planos no separador Planos após alterar o catálogo. A migration 025 cria platform_settings."}
      </p>
    </div>
  );
}
