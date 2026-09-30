"use client";

import { Plus } from "lucide-react";

import { RippleLink } from "@/components/ui/ripple-link";
import { ProjectsList } from "@/features/projects/components/projects-list";
import { useAuth } from "@/components/providers/auth-provider";
import { useI18n } from "@/components/providers/locale-provider";

export default function ProjectsPage() {
  const { user } = useAuth();
  const { t } = useI18n();
  const canCreate = user?.role === "admin" || user?.role === "financial";

  return (
    <div className="mx-auto max-w-[1200px] space-y-5 pb-8">
      <header className="va-dash-enter flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-[var(--foreground)]">{t("projects.title")}</h1>
          <p className="mt-1 text-sm text-[var(--muted)]">
            {canCreate ? t("projects.subtitleAnalyst") : t("projects.subtitleCollaborator")}
          </p>
        </div>
        {canCreate ? (
          <RippleLink href="/projects/new" variant="primary" className="shrink-0">
            <Plus className="h-4 w-4" />
            {t("projects.newProject")}
          </RippleLink>
        ) : null}
      </header>
      <ProjectsList canCreate={canCreate} />
    </div>
  );
}
