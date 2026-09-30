"use client";

import { cn } from "@/lib/utils/cn";

export type ProjectSection = {
  id: string;
  label: string;
  count?: number;
};

export function ProjectSectionNav({
  sections,
  active,
  onChange,
  dense = false,
}: {
  sections: ProjectSection[];
  active: string;
  onChange: (id: string) => void;
  dense?: boolean;
}) {
  return (
    <nav
      className={cn(
        "flex flex-wrap gap-1 rounded-lg border border-zinc-200/80 bg-zinc-50/70",
        dense ? "p-0.5" : "rounded-xl p-1",
      )}
      aria-label="Secções"
    >
      {sections.map((section) => {
        const isActive = active === section.id;
        return (
          <button
            key={section.id}
            type="button"
            onClick={() => onChange(section.id)}
            className={cn(
              "inline-flex items-center gap-1 rounded-lg font-medium transition-all duration-200",
              dense ? "px-2 py-1 text-xs" : "gap-1.5 px-3 py-2 text-sm",
              isActive
                ? "bg-white text-teal-800 shadow-sm ring-1 ring-teal-100"
                : "text-zinc-600 hover:bg-white/70 hover:text-zinc-900",
            )}
          >
            {section.label}
            {section.count != null ? (
              <span
                className={cn(
                  "rounded-full px-1.5 py-0.5 text-[10px] font-bold tabular-nums",
                  isActive ? "bg-teal-100 text-teal-800" : "bg-zinc-200/80 text-zinc-600",
                )}
              >
                {section.count}
              </span>
            ) : null}
          </button>
        );
      })}
    </nav>
  );
}
