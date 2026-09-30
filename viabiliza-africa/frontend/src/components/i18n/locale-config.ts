import type { AppLocale } from "@/i18n";

export type LocaleOption = {
  value: AppLocale;
  label: string;
  name: string;
  /** ISO 3166-1 alpha-2 para renderização da bandeira */
  flag: "pt" | "gb";
};

export const LOCALE_OPTIONS: LocaleOption[] = [
  { value: "pt", label: "PT", name: "Português", flag: "pt" },
  { value: "en", label: "EN", name: "English", flag: "gb" },
];

export function getLocaleOption(locale: AppLocale): LocaleOption {
  return LOCALE_OPTIONS.find((item) => item.value === locale) ?? LOCALE_OPTIONS[0];
}
