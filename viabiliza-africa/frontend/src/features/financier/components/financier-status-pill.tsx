"use client";

import type { MonitoringStatus } from "@/lib/types/financier";
import { cn } from "@/lib/utils/cn";

const STYLES: Record<MonitoringStatus, string> = {
  on_track: "bg-emerald-100 text-emerald-800 ring-emerald-200",
  attention: "bg-amber-100 text-amber-900 ring-amber-200",
  critical: "bg-rose-100 text-rose-800 ring-rose-200",
};

export function FinancierStatusPill({
  status,
  label,
  className,
}: {
  status: MonitoringStatus;
  label?: string;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-bold uppercase tracking-wide ring-1",
        STYLES[status],
        className,
      )}
    >
      <span
        className={cn(
          "mr-1.5 h-1.5 w-1.5 rounded-full",
          status === "on_track" && "bg-emerald-500",
          status === "attention" && "bg-amber-500 animate-pulse",
          status === "critical" && "bg-rose-500 animate-pulse",
        )}
      />
      {label ? label : null}
    </span>
  );
}
