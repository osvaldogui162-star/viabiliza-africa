"use client";

import { useEffect, useMemo, useState } from "react";

import { formatCompactCurrency } from "@/lib/currency/format-display";
import type { DisplayCurrency } from "@/lib/currency";
import type { MonthlyPoint } from "@/features/dashboard/lib/dashboard-analytics";

type ChartMode = "investment" | "projects";

function smoothPath(points: Array<{ x: number; y: number }>) {
  if (points.length === 0) return "";
  if (points.length === 1) return `M ${points[0].x} ${points[0].y}`;

  let d = `M ${points[0].x} ${points[0].y}`;
  for (let i = 0; i < points.length - 1; i += 1) {
    const p0 = points[i];
    const p1 = points[i + 1];
    const cx = (p0.x + p1.x) / 2;
    d += ` C ${cx} ${p0.y}, ${cx} ${p1.y}, ${p1.x} ${p1.y}`;
  }
  return d;
}

function formatValue(value: number, mode: ChartMode, locale: string, currency: DisplayCurrency) {
  if (mode === "investment") return formatCompactCurrency(value, currency, locale);
  return String(value);
}

export function AnimatedAreaChart({
  data,
  mode,
  locale,
  currency,
  active,
}: {
  data: MonthlyPoint[];
  mode: ChartMode;
  locale: string;
  currency: DisplayCurrency;
  active: boolean;
}) {
  const [hovered, setHovered] = useState<number | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (active) {
      const t = setTimeout(() => setReady(true), 80);
      return () => clearTimeout(t);
    }
    setReady(false);
    return undefined;
  }, [active, mode]);

  const layout = useMemo(() => {
    const width = 680;
    const height = 220;
    const pad = { top: 16, right: 16, bottom: 28, left: 12 };
    const innerW = width - pad.left - pad.right;
    const innerH = height - pad.top - pad.bottom;

    const values = data.map((d) => (mode === "investment" ? d.investment : d.projects));
    const max = Math.max(...values, mode === "projects" ? 1 : 1000);

    const coords = data.map((d, i) => {
      const val = mode === "investment" ? d.investment : d.projects;
      return {
        x: pad.left + (i / Math.max(data.length - 1, 1)) * innerW,
        y: pad.top + innerH - (val / max) * innerH,
        label: d.label,
        value: val,
      };
    });

    const linePath = smoothPath(coords);
    const baseline = pad.top + innerH;
    const areaPath = coords.length
      ? `${linePath} L ${coords[coords.length - 1].x} ${baseline} L ${coords[0].x} ${baseline} Z`
      : "";

    return { width, height, pad, innerH, coords, linePath, areaPath, max };
  }, [data, mode]);

  const uid = mode === "investment" ? "inv" : "proj";

  return (
    <div className="relative">
      {hovered != null && layout.coords[hovered] ? (
        <div
          className="pointer-events-none absolute z-10 rounded-lg border border-[var(--border)] bg-white px-2.5 py-1.5 text-xs shadow-lg va-tooltip-in"
          style={{
            left: `${(layout.coords[hovered].x / layout.width) * 100}%`,
            top: 8,
            transform: "translateX(-50%)",
          }}
        >
          <p className="font-semibold text-[var(--foreground)]">{layout.coords[hovered].label}</p>
          <p className="tabular-nums text-[var(--primary)]">
            {formatValue(layout.coords[hovered].value, mode, locale, currency)}
          </p>
        </div>
      ) : null}

      <svg viewBox={`0 0 ${layout.width} ${layout.height}`} className="h-auto w-full" role="img">
        <defs>
          <linearGradient id={`vaArea-${uid}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#14b8a6" stopOpacity="0.35" />
            <stop offset="100%" stopColor="#14b8a6" stopOpacity="0" />
          </linearGradient>
          <linearGradient id={`vaLine-${uid}`} x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#0d9488" />
            <stop offset="100%" stopColor="#10b981" />
          </linearGradient>
        </defs>

        {[0.25, 0.5, 0.75].map((ratio) => (
          <line
            key={ratio}
            x1={layout.pad.left}
            x2={layout.width - layout.pad.right}
            y1={layout.pad.top + layout.innerH * ratio}
            y2={layout.pad.top + layout.innerH * ratio}
            stroke="#e2e8f0"
            strokeWidth="1"
            className="va-grid-line"
          />
        ))}

        <path
          d={layout.areaPath}
          fill={`url(#vaArea-${uid})`}
          className={ready ? "va-chart-area-in" : "opacity-0"}
        />
        <path
          d={layout.linePath}
          fill="none"
          stroke={`url(#vaLine-${uid})`}
          strokeWidth="2.5"
          strokeLinecap="round"
          className={ready ? "va-chart-line-in" : "opacity-0"}
          style={{ "--line-length": 900 } as React.CSSProperties}
        />

        {layout.coords.map((point, i) => (
          <g key={point.label}>
            <circle
              cx={point.x}
              cy={point.y}
              r="14"
              fill="transparent"
              className="cursor-pointer"
              onMouseEnter={() => setHovered(i)}
              onMouseLeave={() => setHovered(null)}
            />
            <circle
              cx={point.x}
              cy={point.y}
              r={hovered === i ? 6 : 4}
              fill="#fff"
              stroke="#0d9488"
              strokeWidth="2"
              className={`transition-all duration-200 ${ready ? "va-point-in" : "opacity-0"}`}
              style={{ animationDelay: `${i * 80 + 400}ms` }}
            />
            {hovered === i ? (
              <circle cx={point.x} cy={point.y} r="10" fill="#14b8a6" opacity="0.15" className="va-pulse-ring" />
            ) : null}
            <text
              x={point.x}
              y={layout.height - 8}
              textAnchor="middle"
              className="fill-[#64748b] text-[10px] font-medium"
            >
              {point.label}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}

export function AnimatedBarChart({
  data,
  mode,
  locale,
  currency,
  active,
}: {
  data: MonthlyPoint[];
  mode: ChartMode;
  locale: string;
  currency: DisplayCurrency;
  active: boolean;
}) {
  const [hovered, setHovered] = useState<number | null>(null);

  const layout = useMemo(() => {
    const width = 680;
    const height = 220;
    const pad = { top: 16, right: 16, bottom: 28, left: 12 };
    const innerW = width - pad.left - pad.right;
    const innerH = height - pad.top - pad.bottom;

    const values = data.map((d) => (mode === "investment" ? d.investment : d.projects));
    const max = Math.max(...values, mode === "projects" ? 1 : 1000);
    const barW = innerW / Math.max(data.length, 1) - 10;

    const bars = data.map((d, i) => {
      const val = mode === "investment" ? d.investment : d.projects;
      const h = (val / max) * innerH;
      const x = pad.left + i * (innerW / data.length) + 5;
      const y = pad.top + innerH - h;
      return { x, y, w: barW, h, label: d.label, value: val };
    });

    return { width, height, pad, innerH, bars };
  }, [data, mode]);

  return (
    <div className="relative">
      {hovered != null && layout.bars[hovered] ? (
        <div
          className="pointer-events-none absolute z-10 rounded-lg border border-[var(--border)] bg-white px-2.5 py-1.5 text-xs shadow-lg va-tooltip-in"
          style={{
            left: `${((layout.bars[hovered].x + layout.bars[hovered].w / 2) / layout.width) * 100}%`,
            top: 8,
            transform: "translateX(-50%)",
          }}
        >
          <p className="font-semibold text-[var(--foreground)]">{layout.bars[hovered].label}</p>
          <p className="tabular-nums text-[var(--primary)]">
            {formatValue(layout.bars[hovered].value, mode, locale, currency)}
          </p>
        </div>
      ) : null}

      <svg viewBox={`0 0 ${layout.width} ${layout.height}`} className="h-auto w-full" role="img">
        <defs>
          <linearGradient id="vaBar" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#10b981" />
            <stop offset="100%" stopColor="#0d9488" />
          </linearGradient>
        </defs>

        {[0.25, 0.5, 0.75].map((ratio) => (
          <line
            key={ratio}
            x1={layout.pad.left}
            x2={layout.width - layout.pad.right}
            y1={layout.pad.top + layout.innerH * ratio}
            y2={layout.pad.top + layout.innerH * ratio}
            stroke="#e2e8f0"
            strokeWidth="1"
          />
        ))}

        {layout.bars.map((bar, i) => (
          <g key={bar.label}>
            <g
              transform={`translate(${bar.x}, ${layout.pad.top + layout.innerH})`}
              onMouseEnter={() => setHovered(i)}
              onMouseLeave={() => setHovered(null)}
            >
              <rect
                x={0}
                y={-bar.h}
                width={bar.w}
                height={bar.h}
                fill="url(#vaBar)"
                rx="4"
                className={active ? "va-bar-grow" : "opacity-0"}
                style={{
                  transformOrigin: "center bottom",
                  animationDelay: `${i * 70}ms`,
                }}
              />
            </g>
            <text
              x={bar.x + bar.w / 2}
              y={layout.height - 8}
              textAnchor="middle"
              className="fill-[#64748b] text-[10px] font-medium"
            >
              {bar.label}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}
