"use client";

import { useId, useMemo } from "react";

import { cn } from "@/lib/utils/cn";

type SparklineProps = {
  data: number[];
  className?: string;
  active?: boolean;
  variant?: "default" | "light";
};

export function Sparkline({ data, className = "", active = true, variant = "default" }: SparklineProps) {
  const uid = useId().replace(/:/g, "");
  const isLight = variant === "light";
  const { linePath, areaPath, length } = useMemo(() => {
    const width = 88;
    const height = 32;
    const pad = 2;
    const innerW = width - pad * 2;
    const innerH = height - pad * 2;
    const max = Math.max(...data, 1);

    const points = data.map((value, i) => ({
      x: pad + (i / Math.max(data.length - 1, 1)) * innerW,
      y: pad + innerH - (value / max) * innerH,
    }));

    let line = "";
    if (points.length === 1) {
      line = `M ${points[0].x} ${points[0].y}`;
    } else if (points.length > 1) {
      line = `M ${points[0].x} ${points[0].y}`;
      for (let i = 0; i < points.length - 1; i += 1) {
        const p0 = points[i];
        const p1 = points[i + 1];
        const cx = (p0.x + p1.x) / 2;
        line += ` C ${cx} ${p0.y}, ${cx} ${p1.y}, ${p1.x} ${p1.y}`;
      }
    }

    const baseline = height - pad;
    const area =
      points.length > 0
        ? `${line} L ${points[points.length - 1].x} ${baseline} L ${points[0].x} ${baseline} Z`
        : "";

    return { linePath: line, areaPath: area, length: 120 };
  }, [data]);

  return (
    <svg viewBox="0 0 88 32" className={cn("h-7 w-[76px] shrink-0", className)} aria-hidden>
      <defs>
        <linearGradient id={`vaSparkArea-${uid}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={isLight ? "#5eead4" : "#14b8a6"} stopOpacity={isLight ? 0.42 : 0.35} />
          <stop offset="100%" stopColor={isLight ? "#5eead4" : "#14b8a6"} stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={areaPath} fill={`url(#vaSparkArea-${uid})`} className={active ? "va-chart-area-in" : ""} />
      <path
        d={linePath}
        fill="none"
        stroke={isLight ? "#99f6e4" : "#0d9488"}
        strokeWidth="1.5"
        strokeLinecap="round"
        className={active ? "va-chart-line-in" : ""}
        style={{ "--line-length": length } as React.CSSProperties}
      />
    </svg>
  );
}
