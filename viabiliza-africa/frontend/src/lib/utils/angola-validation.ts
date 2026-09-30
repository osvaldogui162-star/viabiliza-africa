/** Validadores nacionais angolanos (Angola API). */

export const BI_REGEX = /^\d{9}[A-Za-z]{2}\d{3}$/;

export const LOCAL_PHONE_REGEX = /^9\d{8}$/;

export function normalizeBi(value: string): string {
  return value.trim().toUpperCase().replace(/\s/g, "");
}

export function normalizeLocalPhone(value: string): string {
  let digits = value.replace(/\D/g, "");
  if (digits.startsWith("244") && digits.length >= 12) {
    digits = digits.slice(3);
  }
  if (digits.startsWith("0") && digits.length === 10) {
    digits = digits.slice(1);
  }
  return digits.slice(0, 9);
}

export function isValidBiFormat(value: string): boolean {
  return BI_REGEX.test(normalizeBi(value));
}

export function isValidLocalPhone(value: string): boolean {
  return LOCAL_PHONE_REGEX.test(normalizeLocalPhone(value));
}

export function formatBiInput(value: string): string {
  const raw = normalizeBi(value).replace(/[^0-9A-Z]/g, "");
  const digitsStart = raw.match(/^\d*/)?.[0] ?? "";
  const digits = digitsStart.slice(0, 9);
  const rest = raw.slice(digits.length);
  const letters = rest.replace(/[^A-Z]/g, "").slice(0, 2);
  const tailDigits = rest.slice(letters.length).replace(/\D/g, "").slice(0, 3);
  return `${digits}${letters}${tailDigits}`;
}
