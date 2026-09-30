"use client";

import Link from "next/link";
import { ArrowLeft, Building2, Trash2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  compactProjectLabel,
  projectNamesMatch,
} from "@/features/projects/lib/project-display";
import type { Project } from "@/lib/types/project";
import { cn } from "@/lib/utils/cn";

function statusVariant(status: string): "default" | "success" | "warning" | "info" {
  if (status === "active") return "success";
  if (status === "draft") return "default";
  if (status === "submitted") return "info";
  return "warning";
}

type ProjectDetailHeaderProps = {
  project: Project;
  canDelete: boolean;
  onDelete: () => void;
  backLabel: string;
  deleteLabel: string;
  sharedLabel: string;
  compact?: boolean;
};

export function ProjectDetailHeader({
  project,
  canDelete,
  onDelete,
  backLabel,
  deleteLabel,
  sharedLabel,
  compact = false,
}: ProjectDetailHeaderProps) {
  const displayName = compactProjectLabel(project.name, compact ? 56 : 72);
  const showCompany =
    project.company_name?.trim() &&
    !projectNamesMatch(project.name, project.company_name);

  const metaParts = [
    project.sector_label,
    project.country_label,
    showCompany ? compactProjectLabel(project.company_name!, 36) : null,
  ].filter(Boolean);

  return (
    <div
      className={cn(
        "va-project-hero relative overflow-hidden border-teal-900/10",
        compact
          ? "rounded-t-xl border-x border-t px-3 py-2.5 sm:px-4"
          : "rounded-2xl border px-4 py-4 sm:px-5 sm:py-4",
      )}
    >
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_80%_70%_at_0%_0%,rgba(45,212,191,0.1),transparent_55%)]" />

      <div className="relative flex items-center gap-2 sm:gap-3">
        <Link
          href="/projects"
          className={cn(
            "flex shrink-0 items-center justify-center rounded-lg border border-white/60 bg-white/80 text-zinc-600 shadow-sm transition hover:border-teal-200 hover:bg-white hover:text-teal-700",
            compact ? "h-8 w-8" : "h-9 w-9",
          )}
          aria-label={backLabel}
        >
          <ArrowLeft className="h-3.5 w-3.5" />
        </Link>

        <span
          className={cn(
            "hidden shrink-0 items-center justify-center rounded-lg bg-teal-600/10 text-teal-700 sm:flex",
            compact ? "h-8 w-8" : "h-9 w-9",
          )}
        >
          <Building2 className="h-3.5 w-3.5" />
        </span>

        <div className="min-w-0 flex-1">
          <div className="flex min-w-0 items-center gap-1.5 sm:gap-2">
            <h1
              className={cn(
                "min-w-0 flex-1 truncate font-semibold tracking-tight text-zinc-900",
                compact ? "text-sm sm:text-[0.9375rem]" : "text-base sm:text-lg",
              )}
              title={project.name}
            >
              {displayName}
            </h1>
            <div className="flex shrink-0 flex-wrap items-center gap-1">
              <Badge variant={statusVariant(project.status)} className="text-[10px] px-1.5 py-0">
                {project.status_label}
              </Badge>
              {project.is_shared && !project.is_owner ? (
                <Badge variant="info" className="text-[10px] px-1.5 py-0">
                  {sharedLabel}
                </Badge>
              ) : null}
            </div>
          </div>
          {metaParts.length > 0 ? (
            <p
              className="mt-0.5 truncate text-[11px] text-zinc-500"
              title={metaParts.join(" · ")}
            >
              {metaParts.join(" · ")}
            </p>
          ) : null}
        </div>

        {canDelete ? (
          <Button
            variant="danger"
            size="sm"
            onClick={onDelete}
            className={cn("shrink-0 shadow-sm", compact && "h-8 px-2 text-xs")}
            title={deleteLabel}
          >
            <Trash2 className="h-3.5 w-3.5" />
            <span className={cn(compact ? "hidden sm:inline" : "inline")}>{deleteLabel}</span>
          </Button>
        ) : null}
      </div>
    </div>
  );
}
