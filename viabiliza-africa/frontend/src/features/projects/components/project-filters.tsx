"use client";

import { useEffect, useMemo, useState } from "react";
import { RotateCcw, Search, SlidersHorizontal } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { useI18n } from "@/components/providers/locale-provider";
import type { OwnershipFilter } from "@/features/projects/hooks/use-projects-table";
import { projectsApi } from "@/lib/api/projects-api";
import type { MetadataOption } from "@/lib/types/project";

interface ProjectFiltersProps {
  search: string;
  status: string;
  country: string;
  sector: string;
  currency: string;
  ownership: OwnershipFilter;
  onSearchChange: (value: string) => void;
  onStatusChange: (value: string) => void;
  onCountryChange: (value: string) => void;
  onSectorChange: (value: string) => void;
  onCurrencyChange: (value: string) => void;
  onOwnershipChange: (value: OwnershipFilter) => void;
  onClear: () => void;
  hasFilters: boolean;
}

export function ProjectFilters({
  search,
  status,
  country,
  sector,
  currency,
  ownership,
  onSearchChange,
  onStatusChange,
  onCountryChange,
  onSectorChange,
  onCurrencyChange,
  onOwnershipChange,
  onClear,
  hasFilters,
}: ProjectFiltersProps) {
  const { t, locale } = useI18n();
  const en = locale === "en";
  const [statuses, setStatuses] = useState<MetadataOption[]>([]);
  const [countries, setCountries] = useState<MetadataOption[]>([]);
  const [sectors, setSectors] = useState<MetadataOption[]>([]);

  useEffect(() => {
    void projectsApi.metadata().then((meta) => {
      setStatuses(meta.statuses);
      setCountries(meta.countries);
      setSectors(meta.sectors);
    });
  }, []);

  const currencies = useMemo(
    () => [
      { value: "AOA", label: "AOA — Kwanza" },
      { value: "USD", label: "USD — Dólar" },
      { value: "EUR", label: "EUR — Euro" },
      { value: "ZAR", label: "ZAR — Rand" },
    ],
    [],
  );

  return (
    <div className="va-glass-card va-dash-enter p-3 sm:p-4">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[var(--muted-subtle)]">
          <SlidersHorizontal className="h-3.5 w-3.5" />
          {t("filters.title")}
          {hasFilters ? (
            <span className="rounded-full bg-[var(--accent-soft)] px-2 py-0.5 text-[10px] font-bold text-[#115e59]">
              {t("filters.active")}
            </span>
          ) : null}
        </div>
        {hasFilters ? (
          <Button variant="ghost" size="sm" className="h-8 text-xs" onClick={onClear}>
            <RotateCcw className="h-3.5 w-3.5" />
            {en ? "Clear filters" : "Limpar filtros"}
          </Button>
        ) : null}
      </div>

      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-12">
        <div className="relative lg:col-span-4">
          <Search className="absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-[var(--muted-subtle)]" />
          <Input
            placeholder={t("filters.searchPlaceholder")}
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            className="border-[var(--border)] pl-9"
          />
        </div>
        <Select
          value={status}
          onChange={(e) => onStatusChange(e.target.value)}
          className="lg:col-span-2"
        >
          <option value="">{t("filters.allStatuses")}</option>
          {statuses.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </Select>
        <Select
          value={sector}
          onChange={(e) => onSectorChange(e.target.value)}
          className="lg:col-span-2"
        >
          <option value="">{t("filters.allSectors")}</option>
          {sectors.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </Select>
        <Select
          value={country}
          onChange={(e) => onCountryChange(e.target.value)}
          className="lg:col-span-2"
        >
          <option value="">{t("filters.allCountries")}</option>
          {countries.map((c) => (
            <option key={c.value} value={c.value}>
              {c.label}
            </option>
          ))}
        </Select>
        <Select
          value={currency}
          onChange={(e) => onCurrencyChange(e.target.value)}
          className="lg:col-span-1"
        >
          <option value="">{en ? "Currency" : "Moeda"}</option>
          {currencies.map((c) => (
            <option key={c.value} value={c.value}>
              {c.value}
            </option>
          ))}
        </Select>
        <Select
          value={ownership}
          onChange={(e) => onOwnershipChange(e.target.value as OwnershipFilter)}
          className="lg:col-span-1"
        >
          <option value="all">{en ? "All access" : "Todo acesso"}</option>
          <option value="owned">{en ? "Mine" : "Meus"}</option>
          <option value="shared">{en ? "Shared" : "Partilhados"}</option>
        </Select>
      </div>
    </div>
  );
}
