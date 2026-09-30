import type { ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

export function Card({
  children,
  className,
  variant = "default",
}: {
  children: ReactNode;
  className?: string;
  variant?: "default" | "panel";
}) {
  return (
    <div
      className={cn(
        variant === "panel"
          ? "va-project-panel rounded-xl border border-zinc-200/80 bg-white shadow-sm p-3 sm:p-4"
          : "rounded-xl border bg-white p-5 shadow-sm",
        className,
      )}
    >
      {children}
    </div>
  );
}

export function CardHeader({
  title,
  description,
  action,
  eyebrow,
  compact = false,
}: {
  title: string;
  description?: string;
  action?: ReactNode;
  eyebrow?: string;
  compact?: boolean;
}) {
  return (
    <div
      className={cn(
        "flex items-start justify-between gap-3 border-b border-zinc-100",
        compact ? "mb-3 pb-2" : "mb-5 pb-4",
      )}
    >
      <div className="min-w-0">
        {eyebrow ? (
          <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-teal-700">{eyebrow}</p>
        ) : null}
        <h2 className={cn("font-bold tracking-tight text-zinc-900", compact ? "text-base" : "text-lg")}>
          {title}
        </h2>
        {description ? (
          <p className={cn("text-zinc-500", compact ? "mt-0.5 text-xs" : "mt-1 text-sm")}>{description}</p>
        ) : null}
      </div>
      {action}
    </div>
  );
}
