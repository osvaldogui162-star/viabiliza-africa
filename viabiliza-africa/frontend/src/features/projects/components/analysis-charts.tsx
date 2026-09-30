"use client";

import type { MonteCarloResult, ScenarioAnalysisResult } from "@/lib/types/analysis";
import { cn } from "@/lib/utils/cn";
import { formatNumber } from "@/lib/utils/format";

export function MonteCarloChart({ runs }: { runs: MonteCarloResult[] }) {
  const latest = runs[0];
  if (!latest?.results?.percentiles) return null;

  const p = latest.results.percentiles;
  const bars = [
    { label: "P5", value: p.p5 },
    { label: "P25", value: p.p25 },
    { label: "P50", value: p.p50 },
    { label: "P75", value: p.p75 },
    { label: "P95", value: p.p95 },
  ];
  const max = Math.max(...bars.map((b) => Math.abs(b.value)), 1);

  return (
    <div className="rounded-xl border border-zinc-100 bg-zinc-50/50 p-4">
      <p className="mb-3 text-xs font-bold uppercase tracking-wide text-zinc-500">
        Monte Carlo — percentis VPL ({latest.iterations.toLocaleString()} iter.)
      </p>
      <div className="flex h-36 items-end gap-2">
        {bars.map((b, i) => (
          <div key={b.label} className="flex flex-1 flex-col items-center gap-1">
            <span className="text-[9px] font-semibold text-zinc-500">{formatNumber(b.value)}</span>
            <div
              className="va-bar-grow w-full origin-bottom rounded-t bg-gradient-to-t from-violet-600 to-teal-400"
              style={{ height: `${Math.max(8, (Math.abs(b.value) / max) * 100)}%`, animationDelay: `${i * 40}ms` }}
            />
            <span className="text-[10px] text-zinc-400">{b.label}</span>
          </div>
        ))}
      </div>
      <p className="mt-2 text-center text-xs text-teal-700">
        Prob. VPL &gt; 0: {formatNumber((latest.results.probability_npv_positive ?? 0) * 100)}%
      </p>
    </div>
  );
}

export function ScenarioCompareChart({ data }: { data: ScenarioAnalysisResult }) {
  const scenarios = data.scenarios ?? [];
  if (!scenarios.length) return null;

  const maxAbs = Math.max(...scenarios.map((s) => Math.abs(s.npv)), 1);
  const colors = ["bg-emerald-500", "bg-teal-500", "bg-amber-500", "bg-rose-500"];

  return (
    <div className="rounded-xl border border-zinc-100 bg-white p-4 shadow-sm">
      <p className="mb-3 text-xs font-bold uppercase tracking-wide text-zinc-500">Cenários — VPL comparável</p>
      <div className="space-y-3">
        {scenarios.map((row, i) => (
          <div key={row.code}>
            <div className="mb-1 flex justify-between text-xs">
              <span className="font-semibold text-zinc-700">{row.label}</span>
              <span className="text-zinc-500">
                VPL {formatNumber(row.npv)} · TIR {row.irr != null ? `${formatNumber(row.irr)}%` : "—"}
              </span>
            </div>
            <div className="h-2.5 overflow-hidden rounded-full bg-zinc-100">
              <div
                className={cn("h-full rounded-full transition-all duration-700", colors[i % colors.length])}
                style={{ width: `${Math.min(100, (Math.abs(row.npv) / maxAbs) * 100)}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function CashFlowSparkline({ values, color = "#14b8a6" }: { values: number[]; color?: string }) {
  if (values.length < 2) return null;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const w = 140;
  const h = 40;
  const pts = values
    .map((v, i) => {
      const x = (i / (values.length - 1)) * w;
      const y = h - ((v - min) / range) * h;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg width={w} height={h} className="overflow-visible">
      <polyline fill="none" stroke={color} strokeWidth="2" points={pts} className="va-chart-line-in" />
    </svg>
  );
}
