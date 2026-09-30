"use client";

import Link from "next/link";
import { ArrowUpRight, Building2, Calendar, MapPin, Plus } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { DashboardActionButton } from "@/features/dashboard/components/dashboard-action-button";
import { useI18n } from "@/components/providers/locale-provider";
import type { Project } from "@/lib/types/project";

function statusVariant(status: string): "default" | "success" | "warning" | "info" {
  if (status === "active") return "success";
  if (status === "draft") return "default";
  if (status === "submitted") return "info";
  return "warning";
}

type DashboardRecentProjectsProps = {
  projects: Project[];
  canCreate: boolean;
  total: number;
  enterDelay?: number;
};

export function DashboardRecentProjects({
  projects,
  canCreate,
  total,
  enterDelay = 0,
}: DashboardRecentProjectsProps) {
  const { t, intlLocale, formatMoney } = useI18n();

  return (
    <section className="va-glass-card va-dash-enter overflow-hidden" style={{ animationDelay: `${enterDelay}ms` }}>
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--border)] px-4 py-3">
        <div>
          <h2 className="va-section-title">{t("dashboard.recentProjects")}</h2>
          <p className="va-section-sub">{t("dashboard.recentHint", { total })}</p>
        </div>
        <div className="flex gap-1.5">
          <DashboardActionButton href="/projects" variant="secondary" className="inline-flex items-center gap-1 px-3 py-1.5 text-xs">
            {t("dashboard.viewAll")}
            <ArrowUpRight className="h-3 w-3" />
          </DashboardActionButton>
          {canCreate ? (
            <DashboardActionButton href="/projects/new" variant="primary" className="inline-flex items-center gap-1 px-3 py-1.5 text-xs">
              <Plus className="h-3 w-3" />
              {t("dashboard.new")}
            </DashboardActionButton>
          ) : null}
        </div>
      </div>

      {projects.length === 0 ? (
        <div className="flex flex-col items-center px-4 py-10 text-center">
          <span className="va-icon-box h-12 w-12">
            <Building2 className="h-5 w-5" />
          </span>
          <p className="mt-3 max-w-sm text-sm text-[var(--muted)]">
            {canCreate ? t("dashboard.emptyCanCreate") : t("dashboard.emptyShared")}
          </p>
          {canCreate ? (
            <DashboardActionButton href="/projects/new" variant="primary" className="mt-4 inline-flex items-center gap-1.5">
              <Plus className="h-3.5 w-3.5" />
              {t("dashboard.createProject")}
            </DashboardActionButton>
          ) : null}
        </div>
      ) : (
        <div className="grid gap-2.5 p-3 sm:grid-cols-2 xl:grid-cols-3">
          {projects.map((project, index) => (
            <Link
              key={project.id}
              href={`/projects/${project.id}`}
              className="va-dash-enter group rounded-lg border border-[var(--border)] bg-slate-50/60 p-3 transition duration-200 hover:-translate-y-0.5 hover:border-[var(--accent-border)] hover:bg-white hover:shadow-md hover:shadow-teal-500/5"
              style={{ animationDelay: `${enterDelay + 100 + index * 50}ms` }}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <h3 className="truncate text-sm font-semibold text-[var(--foreground)] transition group-hover:text-[var(--primary)]">
                    {project.name}
                  </h3>
                  <p className="truncate text-[11px] text-[var(--muted)]">{project.company_name}</p>
                </div>
                <Badge variant={statusVariant(project.status)}>{project.status_label}</Badge>
              </div>

              <p className="mt-2 text-base font-bold tabular-nums text-[var(--foreground)]">
                {formatMoney(project.investment_amount, project.currency)}
              </p>

              <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-[11px] text-[var(--muted)]">
                <span className="inline-flex items-center gap-1">
                  <Building2 className="h-3 w-3" />
                  {project.sector_label}
                </span>
                <span className="inline-flex items-center gap-1">
                  <MapPin className="h-3 w-3" />
                  {project.country_label}
                </span>
                <span className="inline-flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  {new Date(project.updated_at).toLocaleDateString(intlLocale)}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
