export const SUPPORTED_CURRENCIES = ["AOA", "USD", "EUR"] as const;

export type DisplayCurrency = (typeof SUPPORTED_CURRENCIES)[number];

export const DEFAULT_CURRENCY: DisplayCurrency = "AOA";

export const CURRENCY_STORAGE_KEY = "viabiliza-currency";

/** Taxas MVP alinhadas com o backend (base AOA). */
export const FX_RATES: Record<string, Record<DisplayCurrency, number>> = {
  AOA: { AOA: 1, USD: 1 / 850, EUR: 1 / 920 },
  USD: { AOA: 850, USD: 1, EUR: 0.92 },
  EUR: { AOA: 920, USD: 1.09, EUR: 1 },
};

export function normalizeCurrency(code: string | null | undefined): DisplayCurrency {
  const upper = (code ?? DEFAULT_CURRENCY).toUpperCase();
  if (upper === "USD" || upper === "EUR" || upper === "AOA") return upper;
  return DEFAULT_CURRENCY;
}

export function convertCurrency(
  amount: number,
  fromCurrency: string,
  toCurrency: DisplayCurrency,
): number {
  const from = normalizeCurrency(fromCurrency);
  if (from === toCurrency) return amount;
  const rate = FX_RATES[from]?.[toCurrency];
  return rate != null ? amount * rate : amount;
}

export function getStoredCurrency(): DisplayCurrency {
  if (typeof window === "undefined") return DEFAULT_CURRENCY;
  return normalizeCurrency(window.localStorage.getItem(CURRENCY_STORAGE_KEY));
}

export function storeCurrency(currency: DisplayCurrency) {
  window.localStorage.setItem(CURRENCY_STORAGE_KEY, currency);
}
