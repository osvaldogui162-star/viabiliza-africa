"use client";

import { ChevronDown, Sparkles } from "lucide-react";
import { useMemo, useState, type Dispatch, type SetStateAction } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import type { AppLocale } from "@/i18n";
import type { AutoIngestionPreview } from "@/lib/types/ingestion";
import { cn } from "@/lib/utils/cn";

export type AutoSelection = { quantity: string; include: boolean };

type AutoIngestionPreviewModalProps = {
  open: boolean;
  onClose: () => void;
  preview: AutoIngestionPreview | null;
  selections: Record<string, AutoSelection>;
  onSelectionsChange: Dispatch<SetStateAction<Record<string, AutoSelection>>>;
  onRun: () => void;
  running: boolean;
  locale: AppLocale;
  t: (key: string) => string;
};

function formatSectorLabel(sector: string) {
  return sector.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function AutoIngestionPreviewModal({
  open,
  onClose,
  preview,
  selections,
  onSelectionsChange,
  onRun,
  running,
  locale,
  t,
}: AutoIngestionPreviewModalProps) {
  const isEn = locale === "en";
  const [sourcesOpen, setSourcesOpen] = useState(false);

  const includedCount = useMemo(
    () => (preview ? preview.items.filter((item) => selections[item.key]?.include !== false).length : 0),
    [preview, selections],
  );

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={
        isEn ? "Sector catalogue — automatic ingestion" : "Catálogo setorial — ingestão automática"
      }
      description={
        isEn
          ? "Adjust quantities and uncheck items before running. The project balance updates automatically."
          : "Ajuste quantidades e desmarque itens antes de executar. O saldo do projecto actualiza automaticamente."
      }
      size="lg"
      bodyClassName="space-y-4"
      footer={
        <div className="flex flex-col-reverse gap-2 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-xs text-zinc-500">
            {includedCount} / {preview?.total_items ?? 0}{" "}
            {isEn ? "items selected" : "itens seleccionados"}
          </p>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={onClose}>
              {t("common.cancel")}
            </Button>
            <Button loading={running} disabled={!preview || includedCount === 0} onClick={onRun}>
              <Sparkles className="h-4 w-4" />{" "}
              {isEn ? "Run automatic ingestion" : "Executar ingestão automática"}
            </Button>
          </div>
        </div>
      }
    >
      {preview ? (
        <>
          <div className="grid gap-2 sm:grid-cols-3">
            <div className="rounded-xl border border-zinc-200/80 bg-zinc-50/70 px-3 py-2.5">
              <p className="text-[10px] font-semibold uppercase tracking-wide text-zinc-500">
                {isEn ? "Sector" : "Sector"}
              </p>
              <p className="mt-0.5 text-sm font-semibold text-zinc-900">
                {formatSectorLabel(preview.sector)}
              </p>
            </div>
            <div className="rounded-xl border border-zinc-200/80 bg-zinc-50/70 px-3 py-2.5">
              <p className="text-[10px] font-semibold uppercase tracking-wide text-zinc-500">
                {isEn ? "Catalogue items" : "Itens do catálogo"}
              </p>
              <p className="mt-0.5 text-sm font-semibold tabular-nums text-zinc-900">
                {preview.total_items}
              </p>
            </div>
            <div className="rounded-xl border border-zinc-200/80 bg-zinc-50/70 px-3 py-2.5">
              <p className="text-[10px] font-semibold uppercase tracking-wide text-zinc-500">
                {isEn ? "Currency" : "Moeda"}
              </p>
              <p className="mt-0.5 text-sm font-semibold text-zinc-900">{preview.currency}</p>
            </div>
          </div>

          {(preview.retail_suppliers_count ?? 0) > 0 || preview.sources_hint.length > 0 ? (
            <div className="overflow-hidden rounded-xl border border-teal-100/80 bg-gradient-to-r from-teal-50/50 to-emerald-50/30">
              <button
                type="button"
                onClick={() => setSourcesOpen((v) => !v)}
                className="flex w-full items-center justify-between gap-3 px-3.5 py-2.5 text-left transition hover:bg-teal-50/60"
              >
                <div className="min-w-0">
                  <p className="text-xs font-semibold text-teal-900">
                    {isEn ? "Data sources" : "Fontes de dados"}
                  </p>
                  <p className="mt-0.5 truncate text-[11px] text-teal-800/80">
                    {preview.retail_suppliers_count
                      ? isEn
                        ? `${preview.retail_suppliers_count} Angolan retail suppliers`
                        : `${preview.retail_suppliers_count} fornecedores de retalho angolanos`
                      : null}
                    {preview.retail_suppliers_count && preview.sources_hint.length ? " · " : null}
                    {preview.sources_hint.length}{" "}
                    {isEn ? "online channels" : "canais online"}
                  </p>
                </div>
                <ChevronDown
                  className={cn(
                    "h-4 w-4 shrink-0 text-teal-700/70 transition-transform duration-200",
                    sourcesOpen && "rotate-180",
                  )}
                />
              </button>
              {sourcesOpen ? (
                <div className="border-t border-teal-100/80 px-3.5 py-3">
                  {preview.retail_suppliers_sample?.length ? (
                    <p className="mb-2 text-[11px] text-zinc-600">
                      <span className="font-medium text-zinc-700">
                        {isEn ? "Retail network" : "Rede de retalho"}:
                      </span>{" "}
                      {(preview.retail_suppliers_sample ?? []).join(", ")}
                    </p>
                  ) : null}
                  <div className="flex flex-wrap gap-1.5">
                    {preview.sources_hint.map((source) => (
                      <span
                        key={source}
                        className="inline-flex rounded-md border border-teal-200/60 bg-white/80 px-2 py-0.5 text-[10px] font-medium text-teal-900"
                      >
                        {source}
                      </span>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          ) : null}

          <div className="flex items-center justify-between gap-2">
            <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
              {isEn ? "Products to include" : "Produtos a incluir"}
            </p>
            <div className="flex gap-1">
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-7 text-xs"
                onClick={() =>
                  onSelectionsChange((prev) => {
                    const next = { ...prev };
                    preview.items.forEach((item) => {
                      const cur = next[item.key] ?? { quantity: item.quantity || "1", include: true };
                      next[item.key] = { ...cur, include: true };
                    });
                    return next;
                  })
                }
              >
                {isEn ? "Select all" : "Seleccionar todos"}
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-7 text-xs"
                onClick={() =>
                  onSelectionsChange((prev) => {
                    const next = { ...prev };
                    preview.items.forEach((item) => {
                      const cur = next[item.key] ?? { quantity: item.quantity || "1", include: true };
                      next[item.key] = { ...cur, include: false };
                    });
                    return next;
                  })
                }
              >
                {isEn ? "Clear all" : "Limpar"}
              </Button>
            </div>
          </div>

          <ul className="va-scroll-panel max-h-[min(52vh,28rem)] space-y-2 rounded-xl border border-zinc-200/80 bg-white p-2">
            {preview.items.map((item) => {
              const sel = selections[item.key] ?? {
                quantity: item.quantity || "1",
                include: true,
              };
              return (
                <li
                  key={item.key}
                  className={cn(
                    "rounded-lg border border-zinc-100 bg-zinc-50/40 p-3 transition",
                    sel.include ? "opacity-100" : "opacity-55",
                  )}
                >
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                    <label className="flex min-w-0 flex-1 cursor-pointer items-start gap-2.5">
                      <input
                        type="checkbox"
                        className="mt-1 h-4 w-4 rounded border-zinc-300 text-teal-600 focus:ring-teal-500"
                        checked={sel.include}
                        onChange={(e) =>
                          onSelectionsChange((prev) => ({
                            ...prev,
                            [item.key]: { ...sel, include: e.target.checked },
                          }))
                        }
                      />
                      <span className="min-w-0">
                        <span className="block text-sm font-medium leading-snug text-zinc-900">
                          {item.description}
                        </span>
                        <span className="mt-1 block text-[11px] leading-relaxed text-zinc-500">
                          {item.category} · {item.unit}
                        </span>
                      </span>
                    </label>
                    <div className="flex shrink-0 items-end gap-2 sm:flex-col sm:items-end">
                      <Badge variant={item.item_type === "capex" ? "info" : "default"}>
                        {item.item_type.toUpperCase()}
                      </Badge>
                      <div className="w-[5.5rem] sm:w-24">
                        <Input
                          label={t("ingestion.quantity")}
                          type="number"
                          min={0.0001}
                          step="any"
                          disabled={!sel.include}
                          value={sel.quantity}
                          onChange={(e) =>
                            onSelectionsChange((prev) => ({
                              ...prev,
                              [item.key]: {
                                ...sel,
                                quantity: e.target.value || "1",
                              },
                            }))
                          }
                        />
                      </div>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        </>
      ) : null}
    </Modal>
  );
}
