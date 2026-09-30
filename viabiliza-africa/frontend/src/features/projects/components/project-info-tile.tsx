"use client";

import type { ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

type ProjectInfoTileProps = {
  label: string;
  value: ReactNode;
  icon?: ReactNode;
  accent?: string;
  className?: string;
};

export function ProjectInfoTile({ label, value, icon, accent = "#2dd4bf", className }: ProjectInfoTileProps) {
  return (
    <div
      className={cn(
        "va-project-info-tile rounded-xl border border-zinc-200/80 bg-gradient-to-br from-white to-zinc-50/80 p-3.5 transition duration-200 hover:border-teal-200/60 hover:shadow-sm",
        className,
      )}
      style={{ borderLeftWidth: 3, borderLeftColor: accent }}
    >
      <div className="flex items-start gap-2.5">
        {icon ? (
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-teal-50 text-teal-700">
            {icon}
          </span>
        ) : null}
        <div className="min-w-0 flex-1">
          <p className="text-[10px] font-semibold uppercase tracking-wide text-zinc-500">{label}</p>
          <div className="mt-1 text-sm font-semibold leading-snug text-zinc-900">{value}</div>
        </div>
      </div>
    </div>
  );
}
