"use client";

import dynamic from "next/dynamic";
import { Plus } from "lucide-react";

import { EmptyState } from "@/components/ui/empty-state";
import { RippleLink } from "@/components/ui/ripple-link";
import { ProjectFilters } from "@/features/projects/components/project-filters";
import { PageLoader } from "@/components/ui/spinner";

const ProjectsTable = dynamic(
  () =>
    import("@/features/projects/components/projects-table").then((m) => ({
      default: m.ProjectsTable,
    })),
  { loading: () => <PageLoader layout="embedded" /> },
);
import { useProjectsTable } from "@/features/projects/hooks/use-projects-table";
import { useI18n } from "@/components/providers/locale-provider";

export function ProjectsList({ canCreate = true }: { canCreate?: boolean }) {
  const { t } = useI18n();
  const table = useProjectsTable();

  const showBlockingLoader = table.loading && table.items.length === 0;

  return (
    <div className="space-y-4 va-dashboard-ready">
      {showBlockingLoader ? (
        <PageLoader message={t("common.loadingProjects")} layout="section" />
      ) : null}
      {!showBlockingLoader ? (
        <>
      <ProjectFilters
        search={table.search}
        status={table.status}
        country={table.country}
        sector={table.sector}
        currency={table.currency}
        ownership={table.ownership}
        onSearchChange={table.setSearch}
        onStatusChange={table.setStatus}
        onCountryChange={table.setCountry}
        onSectorChange={table.setSector}
        onCurrencyChange={table.setCurrency}
        onOwnershipChange={table.setOwnership}
        onClear={table.clearFilters}
        hasFilters={table.hasFilters}
      />

      <p className="text-sm font-medium text-[var(--muted)]">
        {t("projects.found", { count: table.total })}
      </p>

      {table.total === 0 && !table.loading ? (
        <EmptyState
          title={t("projects.notFound")}
          description={canCreate ? t("projects.emptyAnalyst") : t("projects.emptyCollaborator")}
          action={
            canCreate ? (
              <RippleLink href="/projects/new" variant="primary">
                <Plus className="h-4 w-4" />
                {t("projects.newProject")}
              </RippleLink>
            ) : undefined
          }
        />
      ) : (
        <ProjectsTable
          items={table.items}
          total={table.total}
          loading={table.loading}
          refreshing={table.refreshing}
          page={table.page}
          pageCount={table.pageCount}
          pageSize={table.pageSize}
          pageSizes={table.pageSizes}
          onPageChange={table.setPage}
          onPageSizeChange={table.setPageSize}
          sortKey={table.sortKey}
          sortDir={table.sortDir}
          onSort={table.toggleSort}
          selectedIds={table.selectedIds}
          onToggleSelect={table.toggleSelect}
          onToggleSelectAll={table.toggleSelectAll}
          onRefresh={() => void table.refresh()}
          onDeleted={() => void table.refresh()}
        />
      )}
        </>
      ) : null}
    </div>
  );
}
