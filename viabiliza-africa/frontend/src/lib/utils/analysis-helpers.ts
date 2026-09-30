import type { FinancialIndicators, IndicatorItem } from "@/lib/types/analysis";

const SUMMARY_LABELS: Record<string, string> = {
  vpl: "VPL",
  tir: "TIR",
  roi: "ROI",
  roe: "ROE",
  ebitda_margin: "Margem EBITDA",
  payback_years: "Payback",
  is_viable: "Viável",
  indicators_count: "Indicadores",
  horizon_years: "Horizonte",
  initial_investment: "Investimento",
  discount_rate: "Taxa de desconto",
};

export function getIndicatorItems(indicators: FinancialIndicators): IndicatorItem[] {
  if (Array.isArray(indicators.items)) return indicators.items;
  return [];
}

export function getSummaryEntries(
  indicators: FinancialIndicators,
): Array<{ key: string; label: string; value: string | number | boolean | null }> {
  const summary = indicators.summary ?? {};
  const priority = ["vpl", "tir", "roi", "roe", "ebitda_margin", "payback_years", "is_viable"];

  return priority
    .filter((key) => key in summary)
    .map((key) => ({
      key,
      label: SUMMARY_LABELS[key] ?? key.replace(/_/g, " "),
      value: summary[key] as string | number | boolean | null,
    }));
}

export function groupIndicatorsByCategory(
  indicators: FinancialIndicators,
): Record<string, IndicatorItem[]> {
  if (indicators.by_category && Object.keys(indicators.by_category).length > 0) {
    return indicators.by_category;
  }

  const grouped: Record<string, IndicatorItem[]> = {};
  for (const item of getIndicatorItems(indicators)) {
    const category = item.category ?? "outros";
    grouped[category] ??= [];
    grouped[category].push(item);
  }
  return grouped;
}
