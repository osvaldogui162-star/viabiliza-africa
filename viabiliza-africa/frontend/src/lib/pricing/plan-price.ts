import type { BillingPeriod, PricingPromotion, SubscriptionPlan } from "@/lib/types/subscription";

export function periodAoaKey(period: BillingPeriod): keyof SubscriptionPlan {
  if (period === "quarterly") return "price_quarterly_aoa";
  if (period === "semiannual") return "price_semiannual_aoa";
  return "price_yearly_aoa";
}

export function referenceAoaKey(period: BillingPeriod): string {
  if (period === "quarterly") return "reference_quarterly_aoa";
  if (period === "semiannual") return "reference_semiannual_aoa";
  return "reference_yearly_aoa";
}

export function periodSuffix(period: BillingPeriod, locale: "pt" | "en"): string {
  if (locale === "en") {
    if (period === "quarterly") return "/ quarter";
    if (period === "semiannual") return "/ 6 months";
    return "/ year";
  }
  if (period === "quarterly") return " Kz/trimestre";
  if (period === "semiannual") return " Kz/semestre";
  return " Kz/ano";
}

export function periodLabel(period: BillingPeriod, locale: "pt" | "en"): string {
  if (locale === "en") {
    return period === "quarterly" ? "Quarterly" : period === "semiannual" ? "Semiannual" : "Annual";
  }
  return period === "quarterly" ? "Trimestral" : period === "semiannual" ? "Semestral" : "Anual";
}

function coerceAoa(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim()) {
    const normalized = value.replace(/\s/g, "").replace(",", ".");
    const n = Number(normalized);
    return Number.isFinite(n) ? n : null;
  }
  return null;
}

export function getFixedAoa(plan: SubscriptionPlan, period: BillingPeriod): number | null {
  const key = periodAoaKey(period);
  const fromPlan = coerceAoa(plan[key]);
  if (fromPlan != null) return fromPlan;
  const fromFeatures = coerceAoa(plan.features?.[key as keyof typeof plan.features]);
  if (fromFeatures != null) return fromFeatures;
  const preview = plan.pricing_preview?.[period];
  return coerceAoa(preview?.price_fixed_aoa);
}

export function getReferenceAoa(plan: SubscriptionPlan, period: BillingPeriod): number | null {
  const key = referenceAoaKey(period) as keyof SubscriptionPlan;
  const fromPlan = coerceAoa(plan[key]);
  if (fromPlan != null) return fromPlan;
  const fromFeatures = coerceAoa(plan.features?.[key as keyof typeof plan.features]);
  if (fromFeatures != null) return fromFeatures;
  const preview = plan.pricing_preview?.[period];
  return coerceAoa(preview?.price_reference_aoa);
}

export function promotionalAoa(reference: number, discountPct = 20): number {
  return Math.round(reference * (1 - discountPct / 100));
}

export function resolveDisplayAoa(
  plan: SubscriptionPlan,
  period: BillingPeriod,
  promotion?: PricingPromotion | null,
): { pay: number; reference: number | null; promoActive: boolean } {
  const fixed = getFixedAoa(plan, period);
  const reference = getReferenceAoa(plan, period);
  const preview = plan.pricing_preview?.[period];
  const promoActive = Boolean(promotion?.active ?? preview?.promotion_applied);

  if (promoActive && preview?.subtotal != null) {
    const pay = coerceAoa(preview.subtotal);
    if (pay != null) {
      return { pay, reference: reference ?? coerceAoa(preview.price_reference_aoa), promoActive: true };
    }
  }

  if (fixed == null) return { pay: 0, reference, promoActive: false };

  if (promoActive && reference != null) {
    return { pay: promotionalAoa(reference, promotion?.discount_pct ?? 20), reference, promoActive: true };
  }
  return { pay: fixed, reference: promoActive ? reference : null, promoActive };
}

export function formatAoa(amount: number): string {
  return amount.toLocaleString("pt-AO", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
