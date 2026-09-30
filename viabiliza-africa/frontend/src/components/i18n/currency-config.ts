import type { DisplayCurrency } from "@/lib/currency";

export type CurrencyOption = {
  value: DisplayCurrency;
  label: string;
  name: string;
  symbol: string;
};

export const CURRENCY_OPTIONS: CurrencyOption[] = [
  { value: "AOA", label: "AOA", name: "Kwanza (AOA)", symbol: "Kz" },
  { value: "USD", label: "USD", name: "Dólar (USD)", symbol: "$" },
  { value: "EUR", label: "EUR", name: "Euro (EUR)", symbol: "€" },
];

export function getCurrencyOption(code: DisplayCurrency): CurrencyOption {
  return CURRENCY_OPTIONS.find((item) => item.value === code) ?? CURRENCY_OPTIONS[0];
}
