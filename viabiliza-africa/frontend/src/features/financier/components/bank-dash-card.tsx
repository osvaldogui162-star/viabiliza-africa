"use client";

import { cn } from "@/lib/utils/cn";

export function BankDashCard({
  title,
  children,
  className,
  delayMs = 0,
  noPadding,
  quiet,
}: {
  title?: string;
  children: React.ReactNode;
  className?: string;
  delayMs?: number;
  noPadding?: boolean;
  /** Sem faixa lateral animada (painéis especiais) */
  quiet?: boolean;
}) {
  return (
    <article
      className={cn(
        "bank-dash-rise",
        !quiet && "bank-dash-card",
        quiet && "rounded-2xl border border-[var(--border)] bg-[var(--card)] shadow-md",
        !noPadding && "p-5",
        className,
      )}
      style={{ animationDelay: `${delayMs}ms` }}
    >
      {title ? <h2 className="bank-dash-card-title">{title}</h2> : null}
      <div className={title ? "mt-3.5" : undefined}>{children}</div>
    </article>
  );
}

export function BankDashSkeleton() {
  return (
    <div className="bank-fin-grid">
      <div className="bank-fin-area-kpis grid grid-cols-2 gap-3 lg:flex lg:flex-col">
        {[0, 1, 2, 3].map((i) => (
          <div
            key={i}
            className="bank-dash-shimmer h-24 rounded-2xl border border-[var(--border)] bg-zinc-100/80"
            style={{ animationDelay: `${i * 80}ms` }}
          />
        ))}
      </div>
      <div className="bank-fin-area-flux bank-dash-shimmer min-h-[320px] rounded-2xl border border-[var(--border)] bg-zinc-100/80" />
      <div className="bank-fin-area-portfolio bank-dash-shimmer min-h-[420px] rounded-2xl border border-[var(--border)] bg-zinc-100/80" />
      <div className="bank-fin-area-bottom grid gap-3 sm:grid-cols-3">
        {[0, 1, 2].map((i) => (
          <div key={i} className="bank-dash-shimmer h-44 rounded-2xl border border-[var(--border)] bg-zinc-100/80" />
        ))}
      </div>
    </div>
  );
}
