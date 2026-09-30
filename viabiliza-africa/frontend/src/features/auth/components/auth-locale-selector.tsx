"use client";

import { ChevronDown } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { LOCALE_OPTIONS, getLocaleOption } from "@/components/i18n/locale-config";
import { LocaleFlag } from "@/components/i18n/locale-flag";
import { useI18n } from "@/components/providers/locale-provider";
import type { AppLocale } from "@/i18n";
import { cn } from "@/lib/utils/cn";

type AuthLocaleSelectorProps = {
  className?: string;
};

export function AuthLocaleSelector({ className }: AuthLocaleSelectorProps) {
  const { locale, setLocale } = useI18n();
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const current = getLocaleOption(locale);

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
        aria-label="Selecionar idioma"
        onClick={() => setOpen((prev) => !prev)}
        className={cn(
          "inline-flex min-h-11 items-center gap-2.5 rounded-xl border border-zinc-200 bg-white px-3.5 py-2.5 text-base font-semibold text-zinc-800 shadow-md transition sm:min-h-12 sm:gap-3 sm:px-4",
          "hover:border-zinc-300 hover:bg-zinc-50 focus:outline-none focus:ring-2 focus:ring-sky-200",
          open && "border-sky-200 ring-2 ring-sky-100",
        )}
      >
        <LocaleFlag flag={current.flag} className="h-[1.35rem] w-[1.35rem] sm:h-6 sm:w-6" />
        <span className="max-[380px]:hidden">{current.name}</span>
        <span className="hidden max-[380px]:inline">{current.label}</span>
        <ChevronDown
          className={cn(
            "h-4 w-4 shrink-0 text-zinc-500 transition sm:h-[1.125rem] sm:w-[1.125rem]",
            open && "rotate-180",
          )}
        />
      </button>

      {open ? (
        <ul
          role="listbox"
          aria-label="Idiomas disponíveis"
          className="absolute right-0 top-full z-50 mt-2 min-w-[12.5rem] overflow-hidden rounded-xl border border-zinc-200 bg-white py-1.5 shadow-xl"
        >
          {LOCALE_OPTIONS.map((item) => {
            const selected = item.value === locale;
            return (
              <li key={item.value} role="option" aria-selected={selected}>
                <button
                  type="button"
                  onClick={() => {
                    setLocale(item.value as AppLocale);
                    setOpen(false);
                  }}
                  className={cn(
                    "flex w-full items-center gap-3 px-4 py-3 text-left text-base transition",
                    selected
                      ? "bg-sky-50 font-semibold text-sky-700"
                      : "font-medium text-zinc-700 hover:bg-zinc-50",
                  )}
                >
                  <LocaleFlag flag={item.flag} className="h-6 w-6" title={item.name} />
                  <span className="flex-1">{item.name}</span>
                  <span className="text-sm uppercase tracking-wide text-zinc-400">{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      ) : null}
    </div>
  );
}
