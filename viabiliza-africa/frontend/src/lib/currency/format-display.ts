import {
  convertCurrency,
  type DisplayCurrency,
  normalizeCurrency,
} from "@/lib/currency";
import { formatCurrencyAmount } from "@/lib/utils/format";

export function formatDisplayMoney(
  amount: string | number,
  sourceCurrency: string,
  displayCurrency: DisplayCurrency,
  intlLocale: string,
): string {
  const raw = typeof amount === "number" ? amount : Number.parseFloat(String(amount ?? "0"));
  const value = Number.isFinite(raw) ? raw : 0;
  const converted = convertCurrency(value, sourceCurrency, displayCurrency);
  return formatCurrencyAmount(converted, displayCurrency, intlLocale);
}

export function formatCompactCurrency(
  value: number,
  currency: DisplayCurrency,
  locale: string,
): string {
  // Kwanza: número completo (ex.: 10 000 000 Kz), nunca abreviado (10 M Kz).
  if (currency === "AOA") {
    return formatCurrencyAmount(value, currency, locale);
  }

  if (value >= 1_000_000) {
    return new Intl.NumberFormat(locale, {
      style: "currency",
      currency,
      notation: "compact",
      maximumFractionDigits: 1,
    }).format(value);
  }
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(value);
}

export function parseInvestmentToDisplay(
  value: string,
  projectCurrency: string,
  displayCurrency: DisplayCurrency,
): number {
  const amount = Number.parseFloat(value) || 0;
  return convertCurrency(amount, normalizeCurrency(projectCurrency), displayCurrency);
}
