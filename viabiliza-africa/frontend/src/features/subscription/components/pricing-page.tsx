"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ArrowRight,
  Check,
  Loader2,
  Mail,
  Megaphone,
  Shield,
  Sparkles,
  X,
  Zap,
} from "lucide-react";
import { BrandLogo } from "@/components/brand/brand-logo";
import { PageLoader } from "@/components/ui/spinner";
import { PricingHeroCarousel } from "@/features/subscription/components/pricing-hero-carousel";
import { useAuth } from "@/components/providers/auth-provider";
import { subscriptionApi } from "@/lib/api/subscription-api";
import { buildQuery } from "@/lib/api/http-client";
import {
  COMPARISON_ROWS,
  FALLBACK_PLANS,
  mergePlanWithFallback,
  PLAN_FEATURE_LINES,
} from "@/lib/data/pricing-plans";
import {
  formatAoa,
  periodLabel,
  periodSuffix,
  resolveDisplayAoa,
} from "@/lib/pricing/plan-price";
import type {
  BillingPeriod,
  CurrencyDisplay,
  MySubscriptionResponse,
  PricingPromotion,
  SubscriptionPlan,
} from "@/lib/types/subscription";

const CONTACT_EMAIL = "comercial@viabiliza.africa";
const PERIODS: BillingPeriod[] = ["quarterly", "semiannual", "yearly"];

function PlanCard({
  plan,
  period,
  currency,
  promotion,
  isCurrent,
  onSelect,
  index,
}: {
  plan: SubscriptionPlan;
  period: BillingPeriod;
  currency: CurrencyDisplay;
  promotion: PricingPromotion | null;
  isCurrent: boolean;
  onSelect: (plan: SubscriptionPlan) => void;
  index: number;
}) {
  const popular = plan.popular ?? plan.features?.popular;
  const contactOnly = plan.contact_only ?? plan.features?.contact_only;
  const emoji = plan.emoji ?? plan.features?.emoji ?? "";
  const lines = PLAN_FEATURE_LINES[plan.code] ?? [];
  const rec = plan.recommendation;

  const { pay, reference, promoActive } = resolveDisplayAoa(plan, period, promotion);
  const suffix = currency === "AOA" ? periodSuffix(period, "pt") : periodSuffix(period, "en");
  const amount =
    currency === "AOA"
      ? formatAoa(pay)
      : `$${(pay / 1000).toLocaleString("en-US", { maximumFractionDigits: 0 })}`;

  return (
    <article
      className={`pricing-card animate-pricing-rise relative flex flex-col rounded-2xl border bg-white p-6 shadow-sm transition-all duration-500 hover:-translate-y-2 hover:shadow-xl ${
        popular
          ? "border-[#00777f] bg-gradient-to-b from-[#eef8f9] to-white shadow-[0_20px_50px_-20px_rgba(0,119,127,0.35)]"
          : "border-zinc-200"
      } ${isCurrent ? "ring-2 ring-emerald-500 ring-offset-2" : ""}`}
      style={{ animationDelay: `${index * 80}ms` }}
    >
      {popular ? (
        <span className="absolute -top-3.5 left-1/2 -translate-x-1/2 rounded-full bg-[#00777f] px-4 py-1 text-[11px] font-bold tracking-wide text-white shadow-md">
          ⭐ MAIS POPULAR
        </span>
      ) : null}

      {isCurrent ? (
        <span className="absolute right-4 top-4 rounded-full bg-emerald-100 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wide text-emerald-800">
          Plano actual
        </span>
      ) : null}

      <div className="mb-4 text-center">
        <h3 className="font-[family-name:var(--font-poppins)] text-xl font-bold text-[#011636]">
          {emoji} {plan.name}
        </h3>
        <p className="mt-2 min-h-[40px] text-sm leading-relaxed text-zinc-500">{plan.description}</p>
        {rec?.headline_pt ? (
          <p className="mt-2 text-xs font-semibold text-[#00777f]">{rec.headline_pt}</p>
        ) : null}
      </div>

      <div className="mb-1 text-center">
        {promoActive && reference != null && currency === "AOA" ? (
          <p className="text-sm text-zinc-400 line-through">{formatAoa(reference)} Kz</p>
        ) : null}
        <span className="font-[family-name:var(--font-poppins)] text-3xl font-bold text-[#011636] sm:text-4xl">
          {amount}
        </span>
        {currency === "AOA" ? (
          <span className="text-base font-medium text-zinc-500">{suffix}</span>
        ) : (
          <span className="text-base font-medium text-zinc-500">{suffix}</span>
        )}
      </div>

      {promoActive ? (
        <p className="mb-3 text-center text-xs font-semibold text-[#ffa900]">
          Campanha −{promotion?.discount_pct ?? 20}% sobre preço de referência
        </p>
      ) : (
        <p className="mb-3 text-center text-xs text-zinc-500">Preço fixo comercial</p>
      )}

      {rec?.reason_pt ? (
        <p className="mb-4 rounded-xl border border-[#00777f]/20 bg-[#f0fafb] px-3 py-2 text-xs leading-relaxed text-[#011636]">
          {rec.reason_pt}
        </p>
      ) : null}

      <ul className="mb-6 flex-1 space-y-2.5 border-t border-zinc-100 pt-4">
        {lines.map((line) => {
          const negative = line.toLowerCase().startsWith("sem ");
          return (
            <li key={line} className="flex items-start gap-2.5 text-sm text-zinc-600">
              {negative ? (
                <X className="mt-0.5 h-4 w-4 shrink-0 text-red-500" />
              ) : (
                <Check className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />
              )}
              <span>{line}</span>
            </li>
          );
        })}
      </ul>

      {rec?.upgrade_pt ? (
        <p className="mb-3 text-center text-[11px] text-zinc-500">{rec.upgrade_pt}</p>
      ) : null}

      <button
        type="button"
        disabled={isCurrent}
        onClick={() => onSelect(plan)}
        className={`group flex w-full items-center justify-center gap-2 rounded-xl py-3.5 text-sm font-bold transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-60 ${
          popular
            ? "bg-gradient-to-r from-[#00777f] to-[#ffa900] text-white shadow-lg hover:opacity-95"
            : contactOnly
              ? "border-2 border-[#011636] bg-white text-[#011636] hover:bg-[#011636] hover:text-white"
              : "bg-[#011636] text-white hover:bg-[#023048]"
        }`}
      >
        {isCurrent ? (
          "Plano activo"
        ) : contactOnly ? (
          <>
            <Mail className="h-4 w-4" />
            Contactar comercial
          </>
        ) : (
          <>
            Assinar {periodLabel(period, "pt").toLowerCase()}
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
          </>
        )}
      </button>
    </article>
  );
}

export function PricingPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [plans, setPlans] = useState<SubscriptionPlan[]>(FALLBACK_PLANS);
  const [mySub, setMySub] = useState<MySubscriptionResponse | null>(null);
  const [period, setPeriod] = useState<BillingPeriod>("quarterly");
  const [currency, setCurrency] = useState<CurrencyDisplay>("AOA");
  const [promotion, setPromotion] = useState<PricingPromotion | null>(null);
  const [loadingPlans, setLoadingPlans] = useState(true);

  const loadData = useCallback(async () => {
    setLoadingPlans(true);
    try {
      const plansRes = await subscriptionApi.listPlans();
      if (plansRes.items.length > 0) {
        setPlans(plansRes.items.map(mergePlanWithFallback));
      }
      if (plansRes.promotion) setPromotion(plansRes.promotion);
    } catch {
      setPlans(FALLBACK_PLANS);
    } finally {
      setLoadingPlans(false);
    }

    if (isAuthenticated) {
      try {
        const sub = await subscriptionApi.getMySubscription();
        setMySub(sub);
        if (sub.promotion) setPromotion(sub.promotion);
      } catch {
        setMySub(null);
      }
    }
  }, [isAuthenticated]);

  const handleSelect = useCallback(
    (plan: SubscriptionPlan) => {
      const contactOnly = plan.contact_only ?? plan.features?.contact_only;
      if (contactOnly) {
        window.location.href = `mailto:${CONTACT_EMAIL}?subject=Plano ${encodeURIComponent(plan.name)} — ViabilizA+ África`;
        return;
      }
      window.location.href = `/planos/checkout${buildQuery({
        plan: plan.code,
        cycle: period,
        currency,
      })}`;
    },
    [period, currency],
  );

  useEffect(() => {
    if (!authLoading) void loadData();
  }, [authLoading, loadData]);

  const visiblePlans = useMemo(
    () => plans.filter((p) => !p.hidden_from_pricing).sort((a, b) => a.display_order - b.display_order),
    [plans],
  );

  const currentPlanCode = mySub?.plan.code;

  return (
    <div className="pricing-page min-h-screen bg-white font-[family-name:var(--font-inter)] text-zinc-900">
      <header className="sticky top-0 z-50 border-b border-zinc-100 bg-white/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6">
          <BrandLogo variant="full" size="md" theme="light" href="/planos" priority />
          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <Link
                href="/dashboard"
                className="rounded-full bg-[#011636] px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-[#023048]"
              >
                Dashboard
              </Link>
            ) : (
              <Link
                href="/login"
                className="rounded-full bg-[#011636] px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-[#023048]"
              >
                Entrar
              </Link>
            )}
          </div>
        </div>
      </header>

      <section className="mx-auto w-full max-w-7xl px-4 pb-8 pt-8 sm:px-6 sm:pt-10">
        <PricingHeroCarousel
          currentPlanBanner={
            mySub ? (
              <div className="inline-flex flex-wrap items-center justify-center gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 px-5 py-3 text-sm text-emerald-900">
                <Shield className="h-4 w-4" />
                <span>
                  Plano actual: <strong>{mySub.plan.name}</strong>
                </span>
              </div>
            ) : undefined
          }
        />
      </section>

      {promotion?.active ? (
        <section className="mx-auto max-w-4xl px-4 pb-6 sm:px-6">
          <div className="flex flex-col items-center gap-2 rounded-2xl border border-[#ffa900]/40 bg-gradient-to-r from-[#fff8eb] via-white to-[#eef8f9] px-6 py-4 text-center shadow-sm sm:flex-row sm:text-left">
            <Megaphone className="h-8 w-8 shrink-0 text-[#ffa900]" />
            <div className="flex-1">
              <p className="font-[family-name:var(--font-poppins)] text-lg font-bold text-[#011636]">
                Campanha comercial activa — 20% sobre o preço de referência
              </p>
              <p className="mt-1 text-sm text-zinc-600">
                Os preços fixos mantêm-se no catálogo; durante a campanha paga menos com base no
                preço anterior. {promotion.ends_at ? `Válida até ${new Date(promotion.ends_at).toLocaleDateString("pt-AO")}.` : ""}
              </p>
            </div>
            <Sparkles className="hidden h-6 w-6 text-[#00777f] sm:block" />
          </div>
        </section>
      ) : null}

      <section className="mx-auto max-w-3xl px-4 pb-10 sm:px-6">
        <div className="flex flex-col items-center justify-center gap-4 sm:flex-row sm:gap-8">
          <div className="pricing-toggle flex flex-wrap justify-center rounded-full border border-zinc-200 bg-zinc-50 p-1">
            {PERIODS.map((p) => (
              <button
                key={p}
                type="button"
                onClick={() => setPeriod(p)}
                className={`rounded-full px-4 py-2 text-sm font-semibold transition-all duration-300 sm:px-5 ${
                  period === p ? "bg-[#011636] text-white shadow-md" : "text-zinc-600 hover:text-zinc-900"
                }`}
              >
                {periodLabel(p, "pt")}
              </button>
            ))}
          </div>
          <div className="pricing-toggle flex rounded-full border border-zinc-200 bg-zinc-50 p-1">
            {(["AOA", "USD"] as CurrencyDisplay[]).map((c) => (
              <button
                key={c}
                type="button"
                onClick={() => setCurrency(c)}
                className={`rounded-full px-5 py-2 text-sm font-semibold transition-all duration-300 ${
                  currency === c ? "bg-[#00777f] text-white shadow-md" : "text-zinc-600 hover:text-zinc-900"
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 pb-20 sm:px-6">
        <div className="mb-8 flex items-center gap-3">
          <Zap className="h-5 w-5 text-[#ffa900]" />
          <h2 className="font-[family-name:var(--font-poppins)] text-2xl font-bold text-[#011636]">
            Planos ViabilizA+ África
          </h2>
        </div>

        {loadingPlans ? (
          <PageLoader layout="section" />
        ) : (
          <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-5">
            {visiblePlans.map((plan, index) => (
              <PlanCard
                key={plan.id}
                plan={plan}
                period={period}
                currency={currency}
                promotion={promotion}
                isCurrent={currentPlanCode === plan.code}
                onSelect={handleSelect}
                index={index}
              />
            ))}
          </div>
        )}

        <p className="mt-6 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          <strong>Facturação:</strong> Trimestral (90 dias), semestral (180 dias) ou anual (365 dias).
          Valores em AOA; IVA 25% aplicado no checkout AppyPay.
        </p>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
        <h2 className="mb-8 text-center font-[family-name:var(--font-poppins)] text-2xl font-bold text-[#011636]">
          Comparativo de funcionalidades
        </h2>
        <div className="overflow-x-auto rounded-2xl border border-zinc-200 shadow-sm">
          <table className="w-full min-w-[720px] text-sm">
            <thead>
              <tr className="bg-[#011636] text-left text-white">
                <th className="px-4 py-3 font-semibold">Funcionalidade</th>
                <th className="px-4 py-3 text-center font-semibold">Starter</th>
                <th className="px-4 py-3 text-center font-semibold">Business</th>
                <th className="px-4 py-3 text-center font-semibold">Enterprise</th>
                <th className="px-4 py-3 text-center font-semibold">Academia</th>
                <th className="px-4 py-3 text-center font-semibold">Governo</th>
              </tr>
            </thead>
            <tbody>
              {COMPARISON_ROWS.map((row, i) => (
                <tr key={row.label} className={i % 2 === 0 ? "bg-white" : "bg-zinc-50"}>
                  <td className="border-t border-zinc-100 px-4 py-3 font-medium text-zinc-800">
                    {row.label}
                  </td>
                  <td className="border-t border-zinc-100 px-4 py-3 text-center text-zinc-600">{row.starter}</td>
                  <td className="border-t border-zinc-100 px-4 py-3 text-center text-zinc-600">{row.business}</td>
                  <td className="border-t border-zinc-100 px-4 py-3 text-center text-zinc-600">{row.enterprise}</td>
                  <td className="border-t border-zinc-100 px-4 py-3 text-center text-zinc-600">{row.academia}</td>
                  <td className="border-t border-zinc-100 px-4 py-3 text-center text-zinc-600">{row.governo}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <footer className="border-t border-zinc-200 bg-zinc-50 px-4 py-10 text-center sm:px-6">
        <div className="flex justify-center">
          <BrandLogo variant="full" size="md" theme="light" href="/planos" />
        </div>
        <p className="mt-4 text-sm text-zinc-500">Comercialização v2.0 — ciclos trimestral, semestral e anual</p>
        <p className="mt-4 text-xs">
          <a href={`mailto:${CONTACT_EMAIL}`} className="text-[#00777f] hover:underline">
            {CONTACT_EMAIL}
          </a>
        </p>
      </footer>
    </div>
  );
}
