"use client";

import type { LucideIcon } from "lucide-react";
import { BankFinIcon } from "@/features/financier/components/bank-fin-icon";

export function BankDashEmpty({
  icon: Icon,
  title,
  hint,
}: {
  icon: LucideIcon;
  title: string;
  hint?: string;
}) {
  return (
    <div className="bank-dash-empty flex min-h-[140px] flex-col items-center justify-center px-4 py-8 text-center">
      <BankFinIcon icon={Icon} tone="navy" size="lg" pulse className="mb-3" />
      <p className="text-sm font-semibold text-[var(--brand-navy)]">{title}</p>
      {hint ? <p className="mt-1 max-w-xs text-xs leading-relaxed text-[var(--muted)]">{hint}</p> : null}
    </div>
  );
}
