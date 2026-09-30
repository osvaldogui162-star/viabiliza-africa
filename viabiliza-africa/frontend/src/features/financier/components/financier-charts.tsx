"use client";

import { useEffect, useMemo, useState } from "react";
import { useInView } from "@/hooks/use-in-view";
import { BRAND_COLORS } from "@/lib/constants/brand-colors";
import { cn } from "@/lib/utils/cn";

export type ChartSlice = { label: string; value: number; color: string };

export type FinancierChartTheme = "light" | "dark";

const themeStyles = {
  light: {
    track: "#e4e4e7",
    donutHole: "#ffffff",
    donutTrack: "#e2e8f0",
    gaugeText: BRAND_COLORS.navy,
    gaugeSub: "#71717a",
    barBg: "#fafafa",
    trendBg: "from-[#011636]/5 to-teal-50/40",
    card: "border-zinc-100 bg-white text-zinc-800",
    title: "text-zinc-700",
    legend: "text-zinc-800",
    axis: "text-zinc-500",
  },
  dark: {
    track: "rgba(255,255,255,0.12)",
    donutHole: "#023048",
    donutTrack: "rgba(255,255,255,0.08)",
    gaugeText: "#ffffff",
    gaugeSub: "rgba(45,212,191,0.7)",
    barBg: "rgba(0,0,0,0.25)",
    trendBg: "from-teal-500/10 to-indigo-500/10",
    card: "border-white/10 bg-white/5 text-white",
    title: "text-teal-100",
    legend: "text-white",
    axis: "text-teal-200/60",
  },
};

export function DonutChart({
  slices,
  active,
  theme = "light",
  centerLabel,
}: {
  slices: ChartSlice[];
  active: boolean;
  theme?: FinancierChartTheme;
  centerLabel?: string;
}) {
  const t = themeStyles[theme];
  const total = slices.reduce((s, x) => s + x.value, 0) || 1;
  const [animated, setAnimated] = useState(false);
  useEffect(() => {
    if (active) {
      const id = setTimeout(() => setAnimated(true), 80);
      return () => clearTimeout(id);
    }
    setAnimated(false);
    return undefined;
  }, [active, slices]);

  const cx = 100;
  const cy = 100;
  const r = 62;
  const circ = 2 * Math.PI * r;
  let offset = 0;

  return (
    <svg viewBox="0 0 200 200" className="mx-auto h-44 w-44 sm:h-48 sm:w-48">
      <circle cx={cx} cy={cy} r={r} fill="none" stroke={t.donutTrack} strokeWidth="22" />
      {slices.map((seg) => {
        const len = (seg.value / total) * circ;
        const dash = animated ? `${len} ${circ - len}` : `0 ${circ}`;
        const el = (
          <circle
            key={seg.label}
            cx={cx}
            cy={cy}
            r={r}
            fill="none"
            stroke={seg.color}
            strokeWidth="24"
            strokeDasharray={dash}
            strokeDashoffset={-offset}
            strokeLinecap="butt"
            transform={`rotate(-90 ${cx} ${cy})`}
            style={{
              transition: "stroke-dasharray 1.25s cubic-bezier(0.22, 1, 0.36, 1)",
              filter: "drop-shadow(0 1px 1px rgba(1,22,54,0.08))",
            }}
          />
        );
        offset += len;
        return el;
      })}
      <circle cx={cx} cy={cy} r={42} fill={t.donutHole} />
      {centerLabel ? (
        <text
          x={cx}
          y={cy + 4}
          textAnchor="middle"
          className="fill-current text-lg font-bold"
          style={{ fill: t.gaugeText }}
        >
          {centerLabel}
        </text>
      ) : null}
    </svg>
  );
}

export function RadialGauge({
  value,
  max,
  label,
  theme = "light",
  active = true,
}: {
  value: number;
  max: number;
  label: string;
  theme?: FinancierChartTheme;
  active?: boolean;
}) {
  const t = themeStyles[theme];
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  const [shown, setShown] = useState(active ? 0 : pct);
  useEffect(() => {
    if (!active) {
      setShown(pct);
      return;
    }
    let frame = 0;
    let start: number | null = null;
    const tick = (ts: number) => {
      if (start == null) start = ts;
      const p = Math.min((ts - start) / 1200, 1);
      const eased = 1 - (1 - p) ** 3;
      setShown(pct * eased);
      if (p < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [pct, active]);

  const angle = (shown / 100) * 270;
  const stroke =
    pct > 100 ? "#f87171" : pct > 85 ? "#fbbf24" : theme === "dark" ? "#2dd4bf" : "#00777f";

  return (
    <div className="flex flex-col items-center">
      <svg viewBox="0 0 180 120" className="h-32 w-full max-w-[220px]">
        <path
          d="M 20 90 A 70 70 0 1 1 160 90"
          fill="none"
          stroke={t.track}
          strokeWidth="14"
          strokeLinecap="round"
        />
        <path
          d="M 20 90 A 70 70 0 1 1 160 90"
          fill="none"
          stroke={stroke}
          strokeWidth="14"
          strokeLinecap="round"
          strokeDasharray={`${(angle / 270) * 220} 220`}
          style={{ transition: "stroke 0.3s ease" }}
        />
        <text
          x={90}
          y={86}
          textAnchor="middle"
          style={{ fill: t.gaugeText }}
          className="text-2xl font-bold"
        >
          {shown.toFixed(0)}%
        </text>
        <text
          x={90}
          y={108}
          textAnchor="middle"
          style={{ fill: t.gaugeSub }}
          className="text-[9px] font-semibold uppercase"
        >
          {label}
        </text>
      </svg>
    </div>
  );
}

export function BarChart({
  bars,
  theme = "light",
  active = true,
}: {
  bars: ChartSlice[];
  theme?: FinancierChartTheme;
  active?: boolean;
}) {
  const t = themeStyles[theme];
  const max = Math.max(...bars.map((b) => b.value), 1);

  return (
    <div className="flex h-48 items-end justify-around gap-2 px-1 sm:gap-3 sm:px-2">
      {bars.map((bar, i) => (
        <div key={bar.label} className="flex min-w-0 flex-1 flex-col items-center gap-2">
          <div
            className={cn("relative flex h-40 w-full max-w-[80px] items-end justify-center rounded-t-xl")}
            style={{ background: t.barBg }}
          >
            <div
              className={cn("w-full rounded-t-xl shadow-lg", active && "bank-dash-bar")}
              style={{
                height: active ? `${Math.max(6, (bar.value / max) * 100)}%` : "0%",
                background: `linear-gradient(180deg, ${bar.color}ee, ${bar.color})`,
                animationDelay: `${i * 0.12}s`,
              }}
            />
          </div>
          <span className={cn("text-center text-[10px] font-semibold uppercase tracking-wide", t.axis)}>
            {bar.label}
          </span>
        </div>
      ))}
    </div>
  );
}

export function GroupedComparisonChart({
  projects,
  theme = "light",
  active = true,
}: {
  projects: {
    name: string;
    financial_pct: number;
    physical_pct: number;
  }[];
  theme?: FinancierChartTheme;
  active?: boolean;
}) {
  const t = themeStyles[theme];
  const max = 100;

  return (
    <div className="space-y-3">
      {projects.map((p, row) => (
        <div key={p.name} className="grid grid-cols-[minmax(0,1fr)_minmax(0,2fr)] items-center gap-3">
          <p className={cn("truncate text-xs font-semibold", t.legend)} title={p.name}>
            {p.name}
          </p>
          <div className="flex h-10 items-end gap-1">
            {[
              { v: p.financial_pct, color: "#6366f1", key: "fin" },
              { v: p.physical_pct, color: "#2dd4bf", key: "phys" },
            ].map((bar, i) => (
              <div
                key={bar.key}
                className="relative flex h-full flex-1 items-end rounded-t-md"
                style={{ background: t.barBg }}
              >
                <div
                  className={cn("w-full rounded-t-md", active && "bank-dash-bar")}
                  style={{
                    height: active ? `${Math.max(4, (bar.v / max) * 100)}%` : "0%",
                    background: bar.color,
                    animationDelay: `${row * 0.08 + i * 0.06}s`,
                  }}
                />
              </div>
            ))}
          </div>
        </div>
      ))}
      <div className={cn("flex justify-end gap-4 text-[10px] font-semibold uppercase", t.axis)}>
        <span className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-sm bg-indigo-400" /> Financeiro
        </span>
        <span className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-sm bg-teal-400" /> Físico
        </span>
      </div>
    </div>
  );
}

export function TrendChart({
  points,
  formatMoney,
  theme = "light",
}: {
  points: { month: string; amount: number }[];
  formatMoney: (n: number) => string;
  theme?: FinancierChartTheme;
}) {
  const t = themeStyles[theme];
  const { ref, inView } = useInView();
  const max = Math.max(...points.map((p) => p.amount), 1);
  const w = 400;
  const h = 140;
  const pad = 12;

  const coords = useMemo(() => {
    if (points.length === 0) return [];
    return points.map((p, i) => ({
      x: pad + (i / Math.max(points.length - 1, 1)) * (w - pad * 2),
      y: h - pad - (p.amount / max) * (h - pad * 2),
      ...p,
    }));
  }, [points, max]);

  const line =
    coords.length > 0
      ? coords.map((c, i) => `${i === 0 ? "M" : "L"} ${c.x} ${c.y}`).join(" ")
      : "";

  const area =
    coords.length > 0
      ? `${line} L ${coords[coords.length - 1].x} ${h - pad} L ${coords[0].x} ${h - pad} Z`
      : "";

  const stroke = theme === "dark" ? "#2dd4bf" : "#00777f";

  return (
    <div
      ref={ref}
      className={cn("rounded-2xl bg-gradient-to-br p-4", t.trendBg)}
    >
      <svg viewBox={`0 0 ${w} ${h}`} className="h-36 w-full">
        <defs>
          <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={stroke} stopOpacity="0.35" />
            <stop offset="100%" stopColor={stroke} stopOpacity="0" />
          </linearGradient>
        </defs>
        {area ? (
          <path
            d={area}
            fill="url(#trendFill)"
            opacity={inView ? 1 : 0}
            style={{ transition: "opacity 1s ease" }}
          />
        ) : null}
        {coords.map((c, i) => (
          <circle
            key={c.month}
            cx={c.x}
            cy={c.y}
            r={inView ? 5 : 0}
            fill={stroke}
            style={{ transition: `r 0.5s ease ${i * 0.08}s` }}
          />
        ))}
        <path
          d={line}
          fill="none"
          stroke={stroke}
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeDasharray={inView ? "800" : "0 800"}
          style={{ transition: "stroke-dasharray 1.6s cubic-bezier(0.22, 1, 0.36, 1)" }}
        />
      </svg>
      <div className={cn("mt-1 flex justify-between text-[10px] font-medium", t.axis)}>
        {points.map((p) => (
          <span key={p.month}>{p.month.slice(5)}</span>
        ))}
      </div>
      {points.length > 0 ? (
        <p className={cn("mt-2 text-center text-xs", t.axis)}>
          Último mês:{" "}
          <strong className={theme === "dark" ? "text-white" : "text-zinc-800"}>
            {formatMoney(points[points.length - 1]?.amount ?? 0)}
          </strong>
        </p>
      ) : null}
    </div>
  );
}

export function FluxoCaixaGroupedChart({
  points,
  totalInflow,
  formatMoney,
  active = true,
  inflowLabel,
  outflowLabel,
  emptyHint,
}: {
  points: { month: string; amount: number }[];
  totalInflow: number;
  formatMoney: (n: number) => string;
  active?: boolean;
  inflowLabel: string;
  outflowLabel: string;
  emptyHint?: string;
}) {
  const n = Math.max(points.length, 1);
  const inflowPerMonth = totalInflow / n;
  const max = Math.max(...points.map((p) => Math.max(p.amount, inflowPerMonth)), 1);

  if (points.length === 0) {
    const placeholders = ["01", "02", "03", "04", "05", "06"];
    return (
      <div>
        <div className="mb-3 flex flex-wrap gap-4 text-[11px] font-semibold uppercase tracking-wide text-[var(--muted)]">
          <span className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-sm bg-[var(--brand-teal)]" />
            {inflowLabel}
          </span>
          <span className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-sm bg-rose-400" />
            {outflowLabel}
          </span>
        </div>
        <div className="flex h-56 items-end justify-between gap-1">
          {placeholders.map((m, i) => (
            <div key={m} className="flex flex-1 flex-col items-center gap-2">
              <div className="flex h-44 w-full max-w-[72px] items-end justify-center gap-1 rounded-t-lg bg-zinc-100/90 px-0.5 ring-1 ring-zinc-200/80">
                <div
                  className={cn("w-[42%] rounded-t-md bg-gradient-to-t from-[var(--brand-teal)] to-teal-400", active && "bank-dash-bar")}
                  style={{ height: active ? `${22 + (i % 3) * 8}%` : "0%", animationDelay: `${i * 0.08}s` }}
                />
                <div
                  className={cn("w-[42%] rounded-t-md bg-gradient-to-t from-rose-500 to-rose-300", active && "bank-dash-bar")}
                  style={{ height: active ? `${14 + (i % 2) * 6}%` : "0%", animationDelay: `${i * 0.08 + 0.04}s` }}
                />
              </div>
              <span className="text-[10px] font-semibold tabular-nums text-[var(--muted)]">{m}/26</span>
            </div>
          ))}
        </div>
        <p className="mt-3 text-center text-xs text-[var(--muted)]">
          {emptyHint ?? "Sem movimentos mensais registados na carteira."}
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-3 flex flex-wrap gap-4 text-[11px] font-semibold uppercase tracking-wide text-[var(--muted)]">
        <span className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-sm bg-[var(--brand-teal)]" />
          {inflowLabel}
        </span>
        <span className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-sm bg-rose-400" />
          {outflowLabel}
        </span>
      </div>
      <div className="flex h-56 items-end justify-between gap-1 sm:gap-2">
        {points.map((p, i) => {
          const inH = (inflowPerMonth / max) * 100;
          const outH = (p.amount / max) * 100;
          return (
            <div key={p.month} className="flex min-w-0 flex-1 flex-col items-center gap-2">
              <div className="flex h-44 w-full max-w-[72px] items-end justify-center gap-1 rounded-t-lg bg-zinc-50 px-0.5">
                <div
                  className={cn("w-[42%] rounded-t-md bg-gradient-to-t from-[var(--brand-teal)] to-teal-400", active && "bank-dash-bar")}
                  style={{
                    height: active ? `${Math.max(4, inH)}%` : "0%",
                    animationDelay: `${i * 0.1}s`,
                  }}
                  title={formatMoney(inflowPerMonth)}
                />
                <div
                  className={cn("w-[42%] rounded-t-md bg-gradient-to-t from-rose-500 to-rose-300", active && "bank-dash-bar")}
                  style={{
                    height: active ? `${Math.max(4, outH)}%` : "0%",
                    animationDelay: `${i * 0.1 + 0.05}s`,
                  }}
                  title={formatMoney(p.amount)}
                />
              </div>
              <span className="text-[10px] font-semibold tabular-nums text-[var(--muted)]">
                {p.month.slice(2).replace("-", "/")}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function SparklineChart({
  points,
  active = true,
}: {
  points: { month: string; amount: number }[];
  active?: boolean;
}) {
  const max = Math.max(...points.map((p) => p.amount), 1);
  const w = 280;
  const h = 64;
  const pad = 4;
  const coords =
    points.length === 0
      ? []
      : points.map((p, i) => ({
          x: pad + (i / Math.max(points.length - 1, 1)) * (w - pad * 2),
          y: h - pad - (p.amount / max) * (h - pad * 2),
        }));
  const line =
    coords.length > 0 ? coords.map((c, i) => `${i === 0 ? "M" : "L"} ${c.x} ${c.y}`).join(" ") : "";

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="mt-2 h-16 w-full text-[var(--brand-teal)]">
      <path
        d={line}
        fill="none"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeDasharray={active ? "400" : "0 400"}
        style={{ transition: "stroke-dasharray 1.2s ease" }}
      />
    </svg>
  );
}

export function ChartCard({
  title,
  children,
  theme = "light",
  className,
  delayMs = 0,
}: {
  title: string;
  children: React.ReactNode;
  theme?: FinancierChartTheme;
  className?: string;
  delayMs?: number;
}) {
  const t = themeStyles[theme];
  return (
    <article
      className={cn("bank-dash-rise rounded-2xl border p-5 shadow-sm backdrop-blur-sm", t.card, className)}
      style={{ animationDelay: `${delayMs}ms` }}
    >
      <h3 className={cn("text-sm font-semibold", t.title)}>{title}</h3>
      <div className="mt-3">{children}</div>
    </article>
  );
}
