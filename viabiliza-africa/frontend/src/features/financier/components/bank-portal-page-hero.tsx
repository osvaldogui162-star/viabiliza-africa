"use client";

import type { LucideIcon } from "lucide-react";
import { BrandLogo } from "@/components/brand/brand-logo";
import { cn } from "@/lib/utils/cn";

export function BankPortalPageHero({
  eyebrow,
  title,
  subtitle,
  icon: Icon,
  tags,
  aside,
  className,
  compact,
}: {
  eyebrow?: string;
  title: string;
  subtitle?: string;
  icon?: LucideIcon;
  tags?: string[];
  aside?: React.ReactNode;
  className?: string;
  compact?: boolean;
}) {
  return (
    <section
      className={cn(
        "bank-portal-hero-band bank-portal-hero-accent relative overflow-hidden",
        compact ? "px-4 py-6 sm:px-6" : "px-4 py-8 sm:px-6 sm:py-10",
        className,
      )}
    >
      <div className="va-dashboard-hero-overlay pointer-events-none absolute inset-0" aria-hidden />
      <div
        className="pointer-events-none absolute -right-[12%] top-0 h-[130%] w-[42%] bank-portal-gold-slab opacity-[0.22]"
        aria-hidden
      />
      <div className="relative mx-auto flex max-w-7xl flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div className="bank-dash-rise min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-3">
            <BrandLogo variant="mark" size="lg" surface="markWhite" className="bank-dash-pulse-ring shadow-lg ring-2 ring-white/10" />
            <BrandLogo variant="full" size="sm" surface="onDark" className="hidden sm:inline-flex opacity-95" />
          </div>
          {eyebrow ? (
            <p className="mt-4 flex items-center gap-2 text-[11px] font-bold uppercase tracking-[0.22em] text-teal-100/90">
              {Icon ? <Icon className="h-3.5 w-3.5 text-[var(--brand-gold)]" /> : null}
              {eyebrow}
            </p>
          ) : null}
          <h1
            className={cn(
              "font-[family-name:var(--font-poppins)] font-bold tracking-tight text-white",
              compact ? "mt-1 text-2xl sm:text-3xl" : "mt-2 text-3xl sm:text-4xl",
            )}
          >
            {title}
          </h1>
          {subtitle ? (
            <p className="mt-2 max-w-2xl text-sm leading-relaxed text-teal-50/85 sm:text-[0.9375rem]">{subtitle}</p>
          ) : null}
          {tags && tags.length > 0 ? (
            <ul className="mt-4 flex flex-wrap gap-2">
              {tags.map((tag) => (
                <li key={tag} className="bank-portal-tag">
                  {tag}
                </li>
              ))}
            </ul>
          ) : null}
        </div>
        {aside ? (
          <div className="bank-dash-rise shrink-0" style={{ animationDelay: "100ms" }}>
            {aside}
          </div>
        ) : null}
      </div>
    </section>
  );
}

export function BankPortalPageBody({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("relative mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8", className)}>
      <div className="bank-portal-content-rise">{children}</div>
    </div>
  );
}
