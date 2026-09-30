"use client";

import { Building2, MapPin, Share2, Users } from "lucide-react";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { useI18n } from "@/components/providers/locale-provider";
import { cn } from "@/lib/utils/cn";
import type { Project } from "@/lib/types/project";

function statusVariant(status: string): "default" | "success" | "warning" | "info" {
  if (status === "active") return "success";
  if (status === "draft") return "default";
  if (status === "submitted") return "info";
  return "warning";
}

const statusAccent: Record<string, string> = {
  active: "from-emerald-500/15 to-teal-500/5 border-emerald-200/60",
  draft: "from-slate-100 to-white border-slate-200",
  submitted: "from-sky-500/10 to-cyan-500/5 border-sky-200/60",
};

export function ProjectCard({
  project,
  index = 0,
  highlight = false,
}: {
  project: Project;
  index?: number;
  highlight?: boolean;
}) {
  const { t, formatMoney } = useI18n();
  const accent = statusAccent[project.status] ?? statusAccent.draft;

  return (
    <Link
      href={`/projects/${project.id}`}
      className={cn(
        "va-dash-enter group relative block overflow-hidden rounded-xl border bg-gradient-to-br p-[1px] transition-all duration-300",
        "hover:-translate-y-1 hover:shadow-lg hover:shadow-teal-500/10",
        highlight ? "va-row-highlight ring-2 ring-teal-400/40" : accent,
      )}
      style={{ animationDelay: `${80 + index * 50}ms` }}
    >
      <article className="relative h-full rounded-[11px] bg-white p-4">
        <div className="pointer-events-none absolute -right-6 -top-6 h-24 w-24 rounded-full bg-teal-400/10 blur-2xl transition duration-500 group-hover:bg-teal-400/20" />

        <div className="relative flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <div className="mb-2 flex h-9 w-9 items-center justify-center rounded-lg bg-[var(--accent-soft)] text-[var(--primary)] transition duration-300 group-hover:scale-110">
              <Building2 className="h-4 w-4" />
            </div>
            <h3 className="truncate text-base font-bold text-[var(--foreground)] transition group-hover:text-[var(--primary)]">
              {project.name}
            </h3>
            <p className="mt-0.5 truncate text-xs text-[var(--muted)]">{project.company_name}</p>
          </div>
          <Badge variant={statusVariant(project.status)}>{project.status_label}</Badge>
        </div>

        <div className="relative mt-4 flex flex-wrap gap-2">
          <span className="inline-flex items-center gap-1 rounded-md bg-slate-50 px-2 py-1 text-[11px] font-medium text-[var(--muted)]">
            <Building2 className="h-3 w-3 text-[var(--primary)]" />
            {project.sector_label}
          </span>
          <span className="inline-flex items-center gap-1 rounded-md bg-slate-50 px-2 py-1 text-[11px] font-medium text-[var(--muted)]">
            <MapPin className="h-3 w-3 text-[var(--primary)]" />
            {project.country_label}
          </span>
        </div>

        <div className="relative mt-4 flex items-end justify-between gap-2 border-t border-[var(--border)] pt-3">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-wider text-[var(--muted-subtle)]">
              {t("projects.investment")}
            </p>
            <p className="mt-0.5 text-lg font-bold tabular-nums text-[var(--primary)]">
              {formatMoney(project.investment_amount, project.currency)}
            </p>
          </div>
          <div className="flex flex-col items-end gap-1 text-[11px] text-[var(--muted)]">
            {project.is_shared ? (
              <span className="inline-flex items-center gap-1 text-emerald-700">
                <Share2 className="h-3 w-3" />
                {t("projects.sharedWithMe")}
              </span>
            ) : null}
            {project.shares_count > 0 ? (
              <span className="inline-flex items-center gap-1">
                <Users className="h-3 w-3" />
                {project.shares_count} {t("common.collaborators")}
              </span>
            ) : null}
          </div>
        </div>
      </article>
    </Link>
  );
}
