"use client";

import type { ReactNode } from "react";
import { AlertCircle, CheckCircle2, Info, Sparkles } from "lucide-react";

import { cn } from "@/lib/utils/cn";

type CalloutVariant = "info" | "warning" | "success" | "neutral";

const VARIANTS: Record<
  CalloutVariant,
  { icon: typeof Info; className: string; iconClass: string }
> = {
  info: {
    icon: Info,
    className: "border-teal-200/80 bg-gradient-to-r from-teal-50/90 to-white",
    iconClass: "text-teal-700 bg-white",
  },
  warning: {
    icon: AlertCircle,
    className: "border-amber-200/80 bg-gradient-to-r from-amber-50/90 to-white",
    iconClass: "text-amber-700 bg-white",
  },
  success: {
    icon: CheckCircle2,
    className: "border-emerald-200/80 bg-gradient-to-r from-emerald-50/90 to-white",
    iconClass: "text-emerald-700 bg-white",
  },
  neutral: {
    icon: Sparkles,
    className: "border-zinc-200/80 bg-gradient-to-r from-zinc-50/90 to-white",
    iconClass: "text-zinc-600 bg-white",
  },
};

export function ProjectCallout({
  title,
  children,
  variant = "info",
  action,
}: {
  title?: string;
  children: ReactNode;
  variant?: CalloutVariant;
  action?: ReactNode;
}) {
  const config = VARIANTS[variant];
  const Icon = config.icon;

  return (
    <div
      className={cn(
        "flex gap-3 rounded-xl border px-4 py-3.5 shadow-sm",
        config.className,
      )}
    >
      <span
        className={cn(
          "flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-black/5 shadow-sm",
          config.iconClass,
        )}
      >
        <Icon className="h-4 w-4" />
      </span>
      <div className="min-w-0 flex-1">
        {title ? <p className="text-sm font-semibold text-zinc-900">{title}</p> : null}
        <div className={cn("text-sm leading-relaxed text-zinc-700", title && "mt-1")}>
          {children}
        </div>
      </div>
      {action ? <div className="shrink-0 self-center">{action}</div> : null}
    </div>
  );
}
