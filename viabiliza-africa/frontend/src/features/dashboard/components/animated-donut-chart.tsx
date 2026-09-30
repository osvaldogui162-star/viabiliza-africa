"use client";

import { useEffect, useMemo, useState } from "react";

import type { SectorSlice } from "@/features/dashboard/lib/dashboard-analytics";

const SLICE_COLORS = ["#0d9488", "#10b981", "#14b8a6", "#059669", "#047857"];

export function AnimatedDonutChart({
  sectors,
  active,
}: {
  sectors: SectorSlice[];
  active: boolean;
}) {
  const [animated, setAnimated] = useState(false);

  useEffect(() => {
    if (active) {
      const t = setTimeout(() => setAnimated(true), 120);
      return () => clearTimeout(t);
    }
    setAnimated(false);
    return undefined;
  }, [active, sectors]);

  const segments = useMemo(() => {
    const cx = 90;
    const cy = 90;
    const r = 58;
    const circumference = 2 * Math.PI * r;
    let offset = 0;

    return sectors.map((sector, index) => {
      const length = (sector.pct / 100) * circumference;
      const seg = {
        ...sector,
        cx,
        cy,
        r,
        length,
        offset,
        color: SLICE_COLORS[index % SLICE_COLORS.length],
        delay: index * 140,
        circumference,
      };
      offset += length;
      return seg;
    });
  }, [sectors]);

  const total = sectors.reduce((s, x) => s + x.count, 0);

  return (
    <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-start">
      <div className="relative shrink-0">
        <svg viewBox="0 0 180 180" className="h-44 w-44 -rotate-90" role="img">
          <circle cx="90" cy="90" r="58" fill="none" stroke="#f1f5f9" strokeWidth="22" />
          {segments.map((seg) => (
            <circle
              key={seg.label}
              cx={seg.cx}
              cy={seg.cy}
              r={seg.r}
              fill="none"
              stroke={seg.color}
              strokeWidth="22"
              strokeLinecap="round"
              strokeDasharray={`${animated ? seg.length : 0} ${seg.circumference}`}
              strokeDashoffset={-seg.offset}
              className="transition-[stroke-dasharray] duration-1000 ease-out"
              style={{ transitionDelay: `${seg.delay}ms` }}
            />
          ))}
        </svg>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-xl font-bold text-[var(--foreground)] ${animated ? "va-count-glow va-badge-pop" : "opacity-0"}`}>
            {total}
          </span>
          <span className="text-[9px] font-medium uppercase text-[var(--muted)]">total</span>
        </div>
        <div className="pointer-events-none absolute inset-0 rounded-full va-donut-glow" />
      </div>

      <div className="min-w-0 flex-1 space-y-2">
        {segments.map((seg) => (
          <div
            key={seg.label}
            className={`flex items-center gap-2.5 ${animated ? "va-dash-enter" : "opacity-0"}`}
            style={{ animationDelay: `${seg.delay + 200}ms` }}
          >
            <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ backgroundColor: seg.color }} />
            <div className="min-w-0 flex-1">
              <div className="flex items-center justify-between gap-2">
                <p className="truncate text-xs font-medium text-[var(--foreground)]">{seg.label}</p>
                <p className="shrink-0 text-[11px] font-semibold tabular-nums text-[var(--primary)]">
                  {seg.pct}%
                </p>
              </div>
              <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full rounded-full transition-[width] duration-700 ease-out"
                  style={{
                    width: animated ? `${seg.pct}%` : "0%",
                    backgroundColor: seg.color,
                    transitionDelay: `${seg.delay + 100}ms`,
                  }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
