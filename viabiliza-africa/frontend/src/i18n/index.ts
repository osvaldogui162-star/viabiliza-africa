import { en } from "./messages/en";
import { pt, type Messages } from "./messages/pt";

export type AppLocale = "pt" | "en";

export const STORAGE_KEY = "viabiliza-locale";

export const messages: Record<AppLocale, Messages> = { pt, en };

export function getStoredLocale(): AppLocale {
  if (typeof window === "undefined") return "pt";
  const stored = window.localStorage.getItem(STORAGE_KEY);
  return stored === "en" ? "en" : "pt";
}

export function storeLocale(locale: AppLocale) {
  window.localStorage.setItem(STORAGE_KEY, locale);
}

export function getIntlLocale(locale: AppLocale): string {
  return locale === "en" ? "en-US" : "pt-AO";
}

type MessageParams = Record<string, string | number>;

function resolvePath(obj: unknown, path: string): string | undefined {
  const value = path.split(".").reduce<unknown>((current, key) => {
    if (current && typeof current === "object" && key in (current as object)) {
      return (current as Record<string, unknown>)[key];
    }
    return undefined;
  }, obj);
  return typeof value === "string" ? value : undefined;
}

export function translate(
  locale: AppLocale,
  key: string,
  params?: MessageParams,
): string {
  const template = resolvePath(messages[locale], key) ?? resolvePath(messages.pt, key) ?? key;
  if (!params) return template;
  return template.replace(/\{(\w+)\}/g, (_, name: string) =>
    params[name] !== undefined ? String(params[name]) : `{${name}}`,
  );
}
