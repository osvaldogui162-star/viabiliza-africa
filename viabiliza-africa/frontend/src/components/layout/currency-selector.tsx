"use client";

import { ChevronDown } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { CURRENCY_OPTIONS, getCurrencyOption } from "@/components/i18n/currency-config";
import { useI18n } from "@/components/providers/locale-provider";
import type { DisplayCurrency } from "@/lib/currency";
import { cn } from "@/lib/utils/cn";

interface CurrencySelectorProps {
  className?: string;
}

export function CurrencySelector({ className }: CurrencySelectorProps) {
  const { currency, setCurrency } = useI18n();
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const current = getCurrencyOption(currency);

  useEffect(() => {
    function onClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  return (
    <div ref={containerRef} className={cn("relative", className)}>
      <button
        type="button"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label="Selecionar moeda"
        onClick={() => setOpen((prev) => !prev)}
        className={cn(
          "va-btn-interactive inline-flex min-h-11 items-center gap-2 rounded-full border border-zinc-200/90 bg-white px-3 py-2 text-sm font-semibold text-zinc-700 shadow-sm sm:min-h-12 sm:px-3.5",
          "hover:border-zinc-300 hover:bg-zinc-50 focus:outline-none focus:ring-2 focus:ring-emerald-100",
          open && "border-emerald-200 bg-emerald-50/40 ring-2 ring-emerald-100",
        )}
      >
        <span className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-50 text-xs font-bold text-emerald-700">
          {current.symbol}
        </span>
        <span>{current.label}</span>
        <ChevronDown className={cn("h-4 w-4 text-zinc-400 transition", open && "rotate-180")} />
      </button>

      {open ? (
        <div className="va-dropdown-in absolute right-0 z-50 mt-2 w-48 overflow-hidden rounded-xl border border-zinc-200 bg-white py-1.5 shadow-xl shadow-zinc-200/60">
          <ul role="listbox" aria-label="Moedas disponíveis">
            {CURRENCY_OPTIONS.map((item) => {
              const selected = item.value === currency;
              return (
                <li key={item.value} role="option" aria-selected={selected}>
                  <button
                    type="button"
                    onClick={() => {
                      setCurrency(item.value as DisplayCurrency);
                      setOpen(false);
                    }}
                    className={cn(
                      "flex w-full items-center gap-3 px-4 py-2.5 text-left text-sm transition",
                      selected
                        ? "bg-emerald-50 font-semibold text-emerald-800"
                        : "font-medium text-zinc-700 hover:bg-zinc-50",
                    )}
                  >
                    <span className="flex h-7 w-7 items-center justify-center rounded-full bg-zinc-100 text-xs font-bold text-zinc-600">
                      {item.symbol}
                    </span>
                    <span className="flex-1">{item.name}</span>
                    <span className="text-xs uppercase tracking-wide text-zinc-400">{item.label}</span>
                  </button>
                </li>
              );
            })}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
