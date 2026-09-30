const numberFormatters: Record<string, Intl.NumberFormat> = {
  "pt-AO": new Intl.NumberFormat("pt-AO", { maximumFractionDigits: 2 }),
  "en-US": new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }),
};

const currencyFormatters: Record<string, Intl.NumberFormat> = {
  "pt-AO": new Intl.NumberFormat("pt-AO", { style: "decimal", maximumFractionDigits: 0 }),
  "en-US": new Intl.NumberFormat("en-US", { style: "decimal", maximumFractionDigits: 0 }),
};

function getFormatters(intlLocale = "pt-AO") {
  return {
    number: numberFormatters[intlLocale] ?? numberFormatters["pt-AO"],
    currency: currencyFormatters[intlLocale] ?? currencyFormatters["pt-AO"],
  };
}

export function formatNumber(
  value: number | string | null | undefined,
  unit?: string,
  intlLocale = "pt-AO",
): string {
  if (value === null || value === undefined) return "—";
  const num = typeof value === "string" ? Number(value) : value;
  if (Number.isNaN(num)) return String(value);

  const { number: numberFormatter } = getFormatters(intlLocale);
  const yearsLabel = intlLocale.startsWith("en") ? "years" : "anos";

  if (unit === "%") return `${numberFormatter.format(num)}%`;
  if (unit === "AOA" || unit === "USD" || unit === "EUR") {
    const { currency: currencyFormatter } = getFormatters(intlLocale);
    return `${currencyFormatter.format(num)} ${unit}`;
  }
  if (unit === "anos" || unit === "years") return `${numberFormatter.format(num)} ${yearsLabel}`;
  if (unit === "x") return `${numberFormatter.format(num)}x`;

  return numberFormatter.format(num);
}

export function formatIndicatorValue(
  value: number | string | null | undefined,
  unit?: string,
  intlLocale = "pt-AO",
): string {
  return formatNumber(value, unit, intlLocale);
}

export function formatDate(
  value: string | Date,
  intlLocale = "pt-AO",
  options?: Intl.DateTimeFormatOptions,
): string {
  const date = typeof value === "string" ? new Date(value) : value;
  return new Intl.DateTimeFormat(intlLocale, options ?? { dateStyle: "medium" }).format(date);
}

export function formatDateTime(value: string | Date, intlLocale = "pt-AO"): string {
  const date = typeof value === "string" ? new Date(value) : value;
  return new Intl.DateTimeFormat(intlLocale, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export function formatCurrencyAmount(
  amount: string | number,
  currency: string,
  intlLocale = "pt-AO",
): string {
  const value = typeof amount === "number" ? amount : parseFloat(String(amount ?? "0"));
  try {
    return new Intl.NumberFormat(intlLocale, {
      style: "currency",
      currency,
      maximumFractionDigits: 0,
    }).format(Number.isFinite(value) ? value : 0);
  } catch {
    return `${amount ?? "0"} ${currency}`;
  }
}

/** Converte valor formatado (1.500.000,50) para string API (1500000.50). */
export function parseMoneyInput(value: string): string {
  const trimmed = value.trim();
  if (!trimmed) return "";

  let normalized = trimmed.replace(/[^\d.,\-]/g, "");
  const negative = normalized.startsWith("-");
  normalized = normalized.replace(/-/g, "");

  if (normalized.includes(",")) {
    normalized = normalized.replace(/\./g, "").replace(",", ".");
  } else if (normalized.includes(".")) {
    const parts = normalized.split(".");
    if (parts.length > 2) {
      normalized = parts.join("");
    } else {
      const [, decPart = ""] = parts;
      if (decPart.length === 3) {
        normalized = parts.join("");
      }
    }
  }

  const match = normalized.match(/^(\d*)(?:\.(\d*))?$/);
  if (!match) return "";

  const intPart = match[1] ?? "";
  const decPart = match[2];
  if (!intPart && (decPart === undefined || decPart === "")) return "";

  let result: string;
  if (decPart !== undefined && decPart !== "") {
    result = `${intPart || "0"}.${decPart.slice(0, 4)}`;
  } else {
    result = intPart || "0";
  }
  return negative ? `-${result}` : result;
}

/** Formata valor bruto/API para exibição com separador de milhares (1.500.000,50). */
export function formatMoneyInput(
  value: string | number | null | undefined,
  options?: { maxDecimals?: number },
): string {
  if (value === null || value === undefined || value === "") return "";

  const maxDecimals = options?.maxDecimals ?? 2;
  const asString = String(value).trim();
  const raw = /^-?\d+(\.\d+)?$/.test(asString)
    ? asString
    : parseMoneyInput(asString);

  if (!raw || raw === ".") return "";

  const negative = raw.startsWith("-");
  const unsigned = negative ? raw.slice(1) : raw;
  const [intRaw = "0", decRaw] = unsigned.split(".");
  const intPart = intRaw.replace(/^0+(?=\d)/, "") || "0";
  const withDots = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ".");

  let result = withDots;
  if (decRaw !== undefined) {
    const decimals = decRaw.slice(0, maxDecimals);
    result = decimals.length > 0 ? `${withDots},${decimals}` : withDots;
  }

  return negative ? `-${result}` : result;
}

/** Reformata texto enquanto o utilizador digita (mantém vírgula decimal). */
export function maskMoneyTyping(input: string, maxDecimals = 2): string {
  const cleaned = input.replace(/[^\d.,]/g, "");
  if (!cleaned) return "";

  const commaIndex = cleaned.indexOf(",");
  let intDigits: string;
  let decDigits: string | undefined;

  if (commaIndex >= 0) {
    intDigits = cleaned.slice(0, commaIndex).replace(/\D/g, "");
    decDigits = cleaned.slice(commaIndex + 1).replace(/\D/g, "").slice(0, maxDecimals);
  } else {
    intDigits = cleaned.replace(/\D/g, "");
  }

  if (!intDigits && decDigits === undefined) return "";
  const withDots = (intDigits || "0").replace(/\B(?=(\d{3})+(?!\d))/g, ".");

  if (commaIndex >= 0) {
    return `${intDigits ? withDots : "0"},${decDigits ?? ""}`;
  }
  return withDots;
}
