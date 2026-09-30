"use client";

import { ArrowDownRight, PiggyBank, Wallet } from "lucide-react";

import { useI18n } from "@/components/providers/locale-provider";
import type { Project } from "@/lib/types/project";
import { cn } from "@/lib/utils/cn";

type ProjectBalanceCardsProps = {
  project: Project;
  opening: number;
  spent: number;
  remaining: number;
  overBudget: boolean;
  compact?: boolean;
};

export function ProjectBalanceCards({
  project,
  opening,
  spent,
  remaining,
  overBudget,
  compact = false,
}: ProjectBalanceCardsProps) {
  const { t, formatMoney } = useI18n();

  const cards = [
    {
      id: "opening",
      label: t("balance.initialInvestment"),
      value: formatMoney(opening, project.currency),
      sub: project.currency,
      icon: Wallet,
      accent: "#2dd4bf",
      variant: "va-project-stat--0" as const,
    },
    {
      id: "spent",
      label: t("balance.outflows"),
      value: `− ${formatMoney(spent, project.currency)}`,
      sub: compact
        ? `${formatMoney(project.capex_spent ?? "0", project.currency)} / ${formatMoney(project.opex_spent ?? "0", project.currency)}`
        : `CAPEX ${formatMoney(project.capex_spent ?? "0", project.currency)} · OPEX ${formatMoney(project.opex_spent ?? "0", project.currency)}`,
      icon: ArrowDownRight,
      accent: "#fb923c",
      variant: "va-project-stat--1" as const,
    },
    {
      id: "remaining",
      label: t("balance.available"),
      value: formatMoney(remaining, project.currency),
      sub: overBudget ? t("balance.overBudget") : compact ? t("balance.autoUpdate") : t("balance.autoUpdate"),
      icon: PiggyBank,
      accent: overBudget ? "#f87171" : "#34d399",
      variant: overBudget ? ("va-project-stat--alert" as const) : ("va-project-stat--2" as const),
      valueClass: overBudget ? "text-rose-700" : "text-emerald-800",
    },
  ];

  if (compact) {
    return (
      <section
        aria-label={t("balance.title")}
        className="border-x border-b border-teal-900/10 bg-white/90 px-2 py-2 sm:px-3"
      >
        <div className="grid grid-cols-3 divide-x divide-zinc-100 rounded-lg border border-zinc-100/80 bg-zinc-50/50">
          {cards.map((card) => (
            <div key={card.id} className="min-w-0 px-2 py-1.5 sm:px-2.5">
              <p className="truncate text-[9px] font-semibold uppercase tracking-wide text-zinc-500">
                {card.label}
              </p>
              <p
                className={cn(
                  "truncate text-xs font-bold tabular-nums sm:text-sm",
                  card.valueClass ?? "text-zinc-900",
                )}
                title={card.value}
              >
                {card.value}
              </p>
              <p className="truncate text-[9px] text-zinc-400" title={card.sub}>
                {card.sub}
              </p>
            </div>
          ))}
        </div>
      </section>
    );
  }

  return (
    <section aria-label={t("balance.title")}>
      <p className="mb-2 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-zinc-500">
        <Wallet className="h-3 w-3 text-teal-600" />
        {t("balance.title")}
      </p>
      <div className="grid gap-2 sm:grid-cols-3">
        {cards.map((card, index) => {
          const Icon = card.icon;
          return (
            <article
              key={card.id}
              className={cn(
                "va-project-stat group relative overflow-hidden rounded-xl p-3",
                card.variant,
              )}
              style={{ animationDelay: `${index * 120}ms` }}
            >
              <div className="relative flex items-start justify-between gap-2">
                <span
                  className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-black/5 bg-white/70 shadow-sm"
                  style={{ color: card.accent }}
                >
                  <Icon className="h-3.5 w-3.5" strokeWidth={2.25} />
                </span>
              </div>
              <p className="relative mt-2 text-[10px] font-semibold uppercase tracking-wide text-zinc-500">
                {card.label}
              </p>
              <p
                className={cn(
                  "relative mt-0.5 truncate text-lg font-bold tabular-nums tracking-tight",
                  card.valueClass ?? "text-zinc-900",
                )}
                title={card.value}
              >
                {card.value}
              </p>
              <p className="relative mt-0.5 truncate text-[10px] text-zinc-500">{card.sub}</p>
            </article>
          );
        })}
      </div>
    </section>
  );
}
