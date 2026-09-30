"use client";

import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils/cn";

export function BankFinIcon({
  icon: Icon,
  tone = "teal",
  size = "md",
  className,
  pulse,
}: {
  icon: LucideIcon;
  tone?: "teal" | "rose" | "navy" | "gold";
  size?: "sm" | "md" | "lg";
  className?: string;
  pulse?: boolean;
}) {
  const box =
    size === "lg" ? "h-12 w-12" : size === "sm" ? "h-9 w-9" : "h-11 w-11";
  const iconSz = size === "lg" ? "h-6 w-6" : size === "sm" ? "h-4 w-4" : "h-5 w-5";

  return (
    <span
      className={cn(
        "bank-fin-icon inline-flex shrink-0 items-center justify-center rounded-xl shadow-md ring-2 ring-white/80",
        box,
        tone === "teal" && "bg-gradient-to-br from-[var(--brand-teal)] to-teal-700 text-white shadow-teal-900/25",
        tone === "rose" && "bg-gradient-to-br from-rose-600 to-rose-700 text-white shadow-rose-900/25",
        tone === "navy" && "bg-gradient-to-br from-[var(--brand-navy)] to-slate-900 text-white shadow-slate-900/30",
        tone === "gold" && "bg-gradient-to-br from-[var(--brand-gold)] to-amber-600 text-[var(--brand-navy)] shadow-amber-900/20",
        pulse && "bank-fin-icon-pulse",
        className,
      )}
    >
      <Icon className={iconSz} strokeWidth={2.25} aria-hidden />
    </span>
  );
}
