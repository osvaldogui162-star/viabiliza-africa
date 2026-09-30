"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo, useRef, useState } from "react";
import {
  ArrowDown,
  ArrowUp,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  Copy,
  Download,
  ExternalLink,
  MoreHorizontal,
  RefreshCw,
  Share2,
  Trash2,
  Users,
} from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AnchoredPanel } from "@/components/ui/anchored-panel";
import { useAuth } from "@/components/providers/auth-provider";
import { useI18n } from "@/components/providers/locale-provider";
import { compactProjectLabel } from "@/features/projects/lib/project-display";
import { exportProjectsCsv } from "@/features/projects/lib/export-projects-csv";
import type { ProjectSortKey, SortDir } from "@/features/projects/hooks/use-projects-table";
import { formatRelativeTime } from "@/features/admin/lib/admin-audit-utils";
import { ApiError } from "@/lib/api/http-client";
import { projectsApi } from "@/lib/api/projects-api";
import type { Project } from "@/lib/types/project";
import { cn } from "@/lib/utils/cn";

function statusVariant(status: string): "default" | "success" | "warning" | "info" {
  if (status === "active") return "success";
  if (status === "draft") return "default";
  if (status === "submitted") return "info";
  return "warning";
}

function SortIcon({ active, dir }: { active: boolean; dir: SortDir }) {
  if (!active) return <ArrowUpDown className="h-3 w-3 opacity-40" />;
  return dir === "asc" ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />;
}

function RowActionsMenu({
  project,
  canDelete,
  onDeleted,
  en,
}: {
  project: Project;
  canDelete: boolean;
  onDeleted: () => void;
  en: boolean;
}) {
  const [open, setOpen] = useState(false);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const router = useRouter();

  async function handleDelete() {
    if (!confirm(en ? "Delete this project?" : "Excluir este projecto?")) return;
    try {
      await projectsApi.delete(project.id);
      toast.success(en ? "Project deleted" : "Projecto excluído");
      onDeleted();
      setOpen(false);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Delete failed" : "Falha ao excluir");
    }
  }

  async function copyId() {
    try {
      await navigator.clipboard.writeText(project.id);
      toast.success(en ? "ID copied" : "ID copiado");
      setOpen(false);
    } catch {
      toast.error(en ? "Copy failed" : "Falha ao copiar");
    }
  }

  return (
    <>
      <button
        ref={buttonRef}
        type="button"
        onClick={(e) => {
          e.stopPropagation();
          setOpen((v) => !v);
        }}
        className="inline-flex h-8 w-8 items-center justify-center rounded-lg border border-zinc-200 bg-white text-zinc-600 transition hover:bg-zinc-50"
        aria-label={en ? "Actions" : "Acções"}
      >
        <MoreHorizontal className="h-4 w-4" />
      </button>
      <AnchoredPanel
        open={open}
        onClose={() => setOpen(false)}
        anchorRef={buttonRef}
        className="w-44 overflow-hidden rounded-xl border border-zinc-200 bg-white py-1 shadow-xl"
        backdropClassName="bg-transparent"
      >
        <button
          type="button"
          className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-zinc-700 hover:bg-zinc-50"
          onClick={() => {
            setOpen(false);
            router.push(`/projects/${project.id}`);
          }}
        >
          <ExternalLink className="h-3.5 w-3.5" />
          {en ? "Open" : "Abrir"}
        </button>
        <button
          type="button"
          className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-zinc-700 hover:bg-zinc-50"
          onClick={() => void copyId()}
        >
          <Copy className="h-3.5 w-3.5" />
          {en ? "Copy ID" : "Copiar ID"}
        </button>
        {canDelete ? (
          <button
            type="button"
            className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-red-600 hover:bg-red-50"
            onClick={() => void handleDelete()}
          >
            <Trash2 className="h-3.5 w-3.5" />
            {en ? "Delete" : "Excluir"}
          </button>
        ) : null}
      </AnchoredPanel>
    </>
  );
}

type ProjectsTableProps = {
  items: Project[];
  total: number;
  loading: boolean;
  refreshing: boolean;
  page: number;
  pageCount: number;
  pageSize: number;
  pageSizes: readonly number[];
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
  sortKey: ProjectSortKey;
  sortDir: SortDir;
  onSort: (key: ProjectSortKey) => void;
  selectedIds: Set<string>;
  onToggleSelect: (id: string) => void;
  onToggleSelectAll: (ids: string[]) => void;
  onRefresh: () => void;
  onDeleted: () => void;
};

export function ProjectsTable({
  items,
  total,
  loading,
  refreshing,
  page,
  pageCount,
  pageSize,
  pageSizes,
  onPageChange,
  onPageSizeChange,
  sortKey,
  sortDir,
  onSort,
  selectedIds,
  onToggleSelect,
  onToggleSelectAll,
  onRefresh,
  onDeleted,
}: ProjectsTableProps) {
  const { user } = useAuth();
  const { t, locale, formatMoney, intlLocale } = useI18n();
  const en = locale === "en";
  const visibleIds = useMemo(() => items.map((p) => p.id), [items]);
  const allVisibleSelected = visibleIds.length > 0 && visibleIds.every((id) => selectedIds.has(id));
  const someSelected = selectedIds.size > 0;

  const selectedProjects = useMemo(
    () => items.filter((p) => selectedIds.has(p.id)),
    [items, selectedIds],
  );

  function headerBtn(key: ProjectSortKey, label: string, className?: string) {
    return (
      <button
        type="button"
        onClick={() => onSort(key)}
        className={cn(
          "inline-flex items-center gap-1 font-semibold uppercase tracking-wide text-zinc-500 transition hover:text-zinc-800",
          className,
        )}
      >
        {label}
        <SortIcon active={sortKey === key} dir={sortDir} />
      </button>
    );
  }

  const rangeStart = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const rangeEnd = Math.min(page * pageSize, total);

  return (
    <div className="overflow-hidden rounded-xl border border-zinc-200/80 bg-white shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-zinc-100 bg-zinc-50/80 px-3 py-2 sm:px-4">
        <p className="text-xs text-zinc-600">
          {en
            ? `${rangeStart}–${rangeEnd} of ${total}`
            : `${rangeStart}–${rangeEnd} de ${total}`}
          {refreshing ? (
            <span className="ml-2 inline-flex items-center gap-1 text-teal-700">
              <RefreshCw className="h-3 w-3 animate-spin" />
              {t("projects.filtering")}
            </span>
          ) : null}
        </p>
        <div className="flex flex-wrap items-center gap-2">
          {someSelected ? (
            <Button
              variant="outline"
              size="sm"
              className="h-8 text-xs"
              onClick={() => exportProjectsCsv(selectedProjects)}
            >
              <Download className="h-3.5 w-3.5" />
              {en ? `Export (${selectedIds.size})` : `Exportar (${selectedIds.size})`}
            </Button>
          ) : (
            <Button variant="outline" size="sm" className="h-8 text-xs" onClick={() => exportProjectsCsv(items)}>
              <Download className="h-3.5 w-3.5" />
              {en ? "Export page" : "Exportar página"}
            </Button>
          )}
          <Button variant="ghost" size="sm" className="h-8 w-8 p-0" onClick={() => onRefresh()} title={en ? "Refresh" : "Actualizar"}>
            <RefreshCw className={cn("h-4 w-4", refreshing && "animate-spin")} />
          </Button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-[960px] w-full text-sm">
          <thead className="sticky top-0 z-[1] border-b border-zinc-100 bg-white text-left text-[10px]">
            <tr>
              <th className="w-10 p-2.5">
                <input
                  type="checkbox"
                  checked={allVisibleSelected}
                  onChange={() => onToggleSelectAll(visibleIds)}
                  className="h-3.5 w-3.5 rounded border-zinc-300 text-teal-600 focus:ring-teal-500/30"
                  aria-label={en ? "Select all" : "Seleccionar todos"}
                />
              </th>
              <th className="p-2.5">{headerBtn("name", en ? "Project" : "Projecto")}</th>
              <th className="p-2.5">{headerBtn("sector_label", en ? "Sector" : "Sector")}</th>
              <th className="hidden p-2.5 md:table-cell">{headerBtn("country_label", en ? "Country" : "País")}</th>
              <th className="p-2.5 text-right">{headerBtn("investment_amount", en ? "Investment" : "Investimento", "justify-end w-full")}</th>
              <th className="hidden p-2.5 lg:table-cell">{headerBtn("status_label", en ? "Status" : "Estado")}</th>
              <th className="hidden p-2.5 xl:table-cell">{en ? "Access" : "Acesso"}</th>
              <th className="hidden p-2.5 sm:table-cell">{headerBtn("updated_at", en ? "Updated" : "Actualizado")}</th>
              <th className="p-2.5 text-right">{en ? "Actions" : "Acções"}</th>
            </tr>
          </thead>
          <tbody className={cn(loading && "opacity-50")}>
            {items.map((project) => {
              const canDelete =
                project.is_owner &&
                (user?.role === "admin" || user?.role === "financial");
              const remaining = project.remaining_balance != null ? parseFloat(project.remaining_balance) : null;

              return (
                <tr
                  key={project.id}
                  className={cn(
                    "group border-b border-zinc-50 transition hover:bg-teal-50/40",
                    selectedIds.has(project.id) && "bg-teal-50/60",
                  )}
                >
                  <td className="p-2.5">
                    <input
                      type="checkbox"
                      checked={selectedIds.has(project.id)}
                      onChange={() => onToggleSelect(project.id)}
                      onClick={(e) => e.stopPropagation()}
                      className="h-3.5 w-3.5 rounded border-zinc-300 text-teal-600 focus:ring-teal-500/30"
                    />
                  </td>
                  <td className="p-2.5">
                    <Link
                      href={`/projects/${project.id}`}
                      className="block min-w-[12rem] max-w-[20rem]"
                      title={project.name}
                    >
                      <p className="truncate font-semibold text-zinc-900 group-hover:text-teal-800">
                        {compactProjectLabel(project.name, 48)}
                      </p>
                      <p className="truncate text-[11px] text-zinc-500">{project.company_name}</p>
                    </Link>
                  </td>
                  <td className="p-2.5">
                    <span className="inline-flex max-w-[8rem] truncate rounded-md bg-zinc-100 px-2 py-0.5 text-xs font-medium text-zinc-700">
                      {project.sector_label}
                    </span>
                  </td>
                  <td className="hidden p-2.5 md:table-cell">
                    <span className="text-xs text-zinc-600">{project.country_label}</span>
                  </td>
                  <td className="p-2.5 text-right">
                    <p className="font-bold tabular-nums text-teal-800">
                      {formatMoney(project.investment_amount, project.currency)}
                    </p>
                    {remaining != null ? (
                      <p className="text-[10px] tabular-nums text-zinc-500">
                        {en ? "Bal." : "Saldo"} {formatMoney(remaining, project.currency)}
                      </p>
                    ) : null}
                  </td>
                  <td className="hidden p-2.5 lg:table-cell">
                    <Badge variant={statusVariant(project.status)}>{project.status_label}</Badge>
                  </td>
                  <td className="hidden p-2.5 xl:table-cell">
                    <div className="flex flex-col gap-0.5 text-[11px] text-zinc-600">
                      {project.is_shared && !project.is_owner ? (
                        <span className="inline-flex items-center gap-1 text-emerald-700">
                          <Share2 className="h-3 w-3" />
                          {t("projects.sharedWithMe")}
                        </span>
                      ) : (
                        <span>{en ? "Owner" : "Proprietário"}</span>
                      )}
                      {project.shares_count > 0 ? (
                        <span className="inline-flex items-center gap-1">
                          <Users className="h-3 w-3" />
                          {project.shares_count} {t("common.collaborators")}
                        </span>
                      ) : null}
                    </div>
                  </td>
                  <td className="hidden p-2.5 sm:table-cell">
                    <span className="text-xs text-zinc-500" title={project.updated_at}>
                      {formatRelativeTime(project.updated_at, intlLocale)}
                    </span>
                  </td>
                  <td className="p-2.5 text-right">
                    <RowActionsMenu
                      project={project}
                      canDelete={canDelete}
                      onDeleted={onDeleted}
                      en={en}
                    />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {items.length === 0 && !loading ? (
        <p className="px-4 py-10 text-center text-sm text-zinc-500">{t("projects.notFound")}</p>
      ) : null}

      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-zinc-100 bg-zinc-50/60 px-3 py-2.5 sm:px-4">
        <div className="flex items-center gap-2 text-xs text-zinc-600">
          <span>{en ? "Rows" : "Linhas"}</span>
          <select
            value={pageSize}
            onChange={(e) => onPageSizeChange(Number(e.target.value))}
            className="rounded-lg border border-zinc-200 bg-white px-2 py-1 text-xs font-medium text-zinc-800"
          >
            {pageSizes.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-1">
          <Button
            variant="outline"
            size="sm"
            className="h-8 w-8 p-0"
            disabled={page <= 1}
            onClick={() => onPageChange(page - 1)}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          {Array.from({ length: Math.min(pageCount, 5) }, (_, i) => {
            let pageNum: number;
            if (pageCount <= 5) pageNum = i + 1;
            else if (page <= 3) pageNum = i + 1;
            else if (page >= pageCount - 2) pageNum = pageCount - 4 + i;
            else pageNum = page - 2 + i;

            return (
              <button
                key={pageNum}
                type="button"
                onClick={() => onPageChange(pageNum)}
                className={cn(
                  "inline-flex h-8 min-w-8 items-center justify-center rounded-lg px-2 text-xs font-semibold transition",
                  pageNum === page
                    ? "bg-teal-600 text-white shadow-sm"
                    : "text-zinc-600 hover:bg-white",
                )}
              >
                {pageNum}
              </button>
            );
          })}
          <Button
            variant="outline"
            size="sm"
            className="h-8 w-8 p-0"
            disabled={page >= pageCount}
            onClick={() => onPageChange(page + 1)}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
