"use client";

import { useEffect, useRef, useState } from "react";

import { cn } from "@/lib/utils/cn";

export interface Tab {
  id: string;
  label: string;
  badge?: number;
}

export function Tabs({
  tabs,
  active,
  onChange,
  variant = "underline",
  dense = false,
}: {
  tabs: Tab[];
  active: string;
  onChange: (id: string) => void;
  variant?: "underline" | "pills";
  dense?: boolean;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [indicator, setIndicator] = useState({ left: 0, width: 0 });

  useEffect(() => {
    const container = containerRef.current;
    if (!container || variant !== "underline") return;
    const btn = container.querySelector<HTMLButtonElement>(`[data-tab-id="${active}"]`);
    if (!btn) return;
    setIndicator({ left: btn.offsetLeft, width: btn.offsetWidth });
  }, [active, tabs, variant]);

  if (variant === "pills") {
    return (
      <div ref={containerRef} className={cn("flex flex-wrap gap-1", dense ? "p-0.5" : "gap-1.5 p-1")}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            data-tab-id={tab.id}
            data-tour={`tab-${tab.id}`}
            onClick={() => onChange(tab.id)}
            className={cn(
              "rounded-lg font-medium transition-all duration-200",
              dense ? "px-2.5 py-1.5 text-xs" : "px-3.5 py-2 text-sm",
              active === tab.id
                ? "bg-teal-600 text-white shadow-sm shadow-teal-600/25"
                : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900",
            )}
          >
            {tab.label}
            {tab.badge != null && tab.badge > 0 ? (
              <span
                className={cn(
                  "ml-1.5 inline-flex h-5 min-w-5 items-center justify-center rounded-full px-1 text-[10px] font-bold",
                  active === tab.id ? "bg-white/25 text-white" : "bg-rose-500 text-white",
                )}
              >
                {tab.badge > 9 ? "9+" : tab.badge}
              </span>
            ) : null}
          </button>
        ))}
      </div>
    );
  }

  return (
    <div ref={containerRef} className="relative flex flex-wrap gap-1 border-b border-[var(--border)]">
      <span
        className="pointer-events-none absolute bottom-0 h-0.5 rounded-full bg-[var(--primary)] transition-all duration-300 ease-out"
        style={{ left: indicator.left, width: indicator.width }}
      />
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          data-tab-id={tab.id}
          data-tour={`tab-${tab.id}`}
          onClick={() => onChange(tab.id)}
          className={cn(
            "relative px-4 py-2.5 text-sm font-medium transition-colors duration-200",
            active === tab.id
              ? "text-[var(--primary)]"
              : "text-[var(--muted)] hover:text-[var(--foreground)]",
          )}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
