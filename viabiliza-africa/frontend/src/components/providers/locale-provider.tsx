"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { toast } from "sonner";

import {
  getIntlLocale,
  getStoredLocale,
  storeLocale,
  translate,
  type AppLocale,
} from "@/i18n";
import { authApi } from "@/lib/api/auth-api";
import {
  DEFAULT_CURRENCY,
  getStoredCurrency,
  normalizeCurrency,
  storeCurrency,
  type DisplayCurrency,
} from "@/lib/currency";
import {
  formatCompactCurrency,
  formatDisplayMoney,
} from "@/lib/currency/format-display";

interface LocaleContextValue {
  locale: AppLocale;
  setLocale: (locale: AppLocale) => void;
  currency: DisplayCurrency;
  setCurrency: (currency: DisplayCurrency) => void;
  t: (key: string, params?: Record<string, string | number>) => string;
  intlLocale: string;
  formatMoney: (amount: string | number, sourceCurrency?: string) => string;
  formatCompactMoney: (amount: number) => string;
}

const LocaleContext = createContext<LocaleContextValue | null>(null);

export function LocaleProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<AppLocale>("pt");
  const [currency, setCurrencyState] = useState<DisplayCurrency>(DEFAULT_CURRENCY);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setLocaleState(getStoredLocale());
    setCurrencyState(getStoredCurrency());
    setReady(true);
  }, []);

  useEffect(() => {
    if (!ready) return;
    document.documentElement.lang = locale === "en" ? "en" : "pt";
  }, [locale, ready]);

  useEffect(() => {
    if (!ready) return;
    let cancelled = false;
    async function syncFromProfile() {
      try {
        const me = await authApi.me();
        if (cancelled) return;
        if (me.preferred_currency) {
          const next = normalizeCurrency(me.preferred_currency);
          setCurrencyState(next);
          storeCurrency(next);
        }
      } catch {
        // sessão não autenticada ou backend indisponível — mantém localStorage
      }
    }
    void syncFromProfile();
    return () => {
      cancelled = true;
    };
  }, [ready]);

  const setLocale = useCallback((next: AppLocale) => {
    setLocaleState(next);
    storeLocale(next);
    toast.message(translate(next, "common.localeChanged"));
  }, []);

  const setCurrency = useCallback((next: DisplayCurrency) => {
    const normalized = normalizeCurrency(next);
    setCurrencyState(normalized);
    storeCurrency(normalized);
    setLocaleState((currentLocale) => {
      toast.message(translate(currentLocale, "common.currencyChanged", { currency: normalized }));
      return currentLocale;
    });
    void authApi.updatePreferences({ preferred_currency: normalized }).catch(() => {
      // preferência local mantém-se mesmo offline
    });
  }, []);

  const intlLocale = getIntlLocale(locale);

  const formatMoney = useCallback(
    (amount: string | number, sourceCurrency?: string) =>
      formatDisplayMoney(amount, sourceCurrency ?? currency, currency, intlLocale),
    [currency, intlLocale],
  );

  const formatCompactMoney = useCallback(
    (amount: number) => formatCompactCurrency(amount, currency, intlLocale),
    [currency, intlLocale],
  );

  const value = useMemo<LocaleContextValue>(
    () => ({
      locale,
      setLocale,
      currency,
      setCurrency,
      t: (key, params) => translate(locale, key, params),
      intlLocale,
      formatMoney,
      formatCompactMoney,
    }),
    [locale, setLocale, currency, setCurrency, intlLocale, formatMoney, formatCompactMoney],
  );

  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
}

export function useI18n() {
  const ctx = useContext(LocaleContext);
  if (!ctx) {
    throw new Error("useI18n must be used within LocaleProvider");
  }
  return ctx;
}
