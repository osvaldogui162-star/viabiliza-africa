"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";

import { PageLoader } from "@/components/ui/spinner";
import { Tabs } from "@/components/ui/tabs";
import { useAuth } from "@/components/providers/auth-provider";
import { useI18n } from "@/components/providers/locale-provider";
import { ProjectBalanceCards } from "@/features/projects/components/project-balance-cards";
import { ProjectDetailHeader } from "@/features/projects/components/project-detail-header";
import { OverviewTab } from "@/features/projects/components/project-tabs/overview-tab";
import { useProjectChatAlerts } from "@/features/collaboration/hooks/use-project-chat-alerts";
import { ApiError } from "@/lib/api/http-client";
import { projectsApi } from "@/lib/api/projects-api";
import type { Project } from "@/lib/types/project";
import { projectTabAllowed, type ProjectTabId } from "@/lib/project-access";
import { cn } from "@/lib/utils/cn";

const IngestionTab = dynamic(
  () =>
    import("@/features/projects/components/project-tabs/ingestion-tab").then((m) => ({
      default: m.IngestionTab,
    })),
  { loading: () => <PageLoader /> },
);

const AnalysisTab = dynamic(
  () =>
    import("@/features/projects/components/project-tabs/analysis-tab").then((m) => ({
      default: m.AnalysisTab,
    })),
  { loading: () => <PageLoader /> },
);

const CollaborationTab = dynamic(
  () =>
    import("@/features/projects/components/project-tabs/collaboration-tab").then((m) => ({
      default: m.CollaborationTab,
    })),
  { loading: () => <PageLoader /> },
);

const ReportsTab = dynamic(
  () =>
    import("@/features/projects/components/project-tabs/reports-tab").then((m) => ({
      default: m.ReportsTab,
    })),
  { loading: () => <PageLoader /> },
);

const ProjectFinancingTab = dynamic(
  () =>
    import("@/features/financier/components/project-financing-tab").then((m) => ({
      default: m.ProjectFinancingTab,
    })),
  { loading: () => <PageLoader /> },
);

export default function ProjectDetailPage({ projectId: initialId }: { projectId: string }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user } = useAuth();
  const { t } = useI18n();
  const [projectId] = useState<string>(initialId);
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const activeTab = searchParams.get("tab") ?? "overview";
  const chatTabActive = activeTab === "collaboration";
  const { unread: chatUnread } = useProjectChatAlerts(projectId, chatTabActive);

  const allTabDefs = useMemo(
    () => [
      { id: "overview" as const, label: t("projectTabs.overview") },
      { id: "ingestion" as const, label: t("projectTabs.ingestion") },
      { id: "analysis" as const, label: t("projectTabs.analysis") },
      {
        id: "collaboration" as const,
        label: t("projectTabs.collaboration"),
        badge: chatUnread || undefined,
      },
      { id: "reports" as const, label: t("projectTabs.reports") },
      { id: "financing" as const, label: t("projectTabs.financing") },
    ],
    [t, chatUnread],
  );

  const tabs = useMemo(() => {
    if (!project) return allTabDefs;
    return allTabDefs.filter((tab) =>
      projectTabAllowed(project, tab.id as ProjectTabId, user?.role),
    );
  }, [allTabDefs, project, user?.role]);

  const loadProject = useCallback(async (opts?: { silent?: boolean }) => {
    if (!opts?.silent) setLoading(true);
    try {
      const data = await projectsApi.get(projectId);
      setProject(data);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("projects.notFoundError"));
      router.push("/projects");
    } finally {
      if (!opts?.silent) setLoading(false);
    }
  }, [projectId, router, t]);

  const refreshBalance = useCallback(async () => {
    try {
      const data = await projectsApi.get(projectId);
      setProject(data);
    } catch {
      /* balance updates on next load */
    }
  }, [projectId]);

  useEffect(() => {
    void loadProject();
    const tourTab = sessionStorage.getItem("va-tour-tab");
    if (tourTab) {
      router.push(`/projects/${projectId}?tab=${tourTab}`);
    }
  }, [loadProject, projectId, router]);

  useEffect(() => {
    if (!project || loading) return;
    const tabId = (activeTab || "overview") as ProjectTabId;
    if (!projectTabAllowed(project, tabId, user?.role)) {
      const fallback = allTabDefs.find((tab) =>
        projectTabAllowed(project, tab.id as ProjectTabId, user?.role),
      );
      if (fallback && fallback.id !== tabId) {
        router.replace(`/projects/${projectId}?tab=${fallback.id}`);
      }
    }
  }, [activeTab, allTabDefs, loading, project, projectId, router, user?.role]);

  function setTab(tab: string) {
    router.push(`/projects/${projectId}?tab=${tab}`);
  }

  async function handleDelete() {
    if (!project || !confirm(t("projects.deleteConfirm"))) return;
    try {
      await projectsApi.delete(project.id);
      toast.success(t("projects.deleted"));
      router.push("/projects");
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("projects.deleteError"));
    }
  }

  if (!project && loading) {
    return <PageLoader message={t("common.loadingProject")} layout="embedded" />;
  }
  if (!project) return null;

  const canDelete =
    user?.role === "admin" || (user?.role === "financial" && project.is_owner);

  const opening = parseFloat(project.investment_amount || "0") || 0;
  const spent = parseFloat(project.spent_total || "0") || 0;
  const remaining =
    project.remaining_balance != null
      ? parseFloat(project.remaining_balance)
      : opening - spent;
  const overBudget = remaining < 0;
  const compactContext = activeTab === "ingestion" || activeTab === "analysis" || activeTab === "collaboration";
  const tabAllowed = projectTabAllowed(project, activeTab as ProjectTabId, user?.role);
  const collaboratorRoleLabel = project.my_access?.job_title;

  return (
    <div className={cn("va-project-detail mx-auto max-w-6xl pb-8", compactContext ? "space-y-3" : "space-y-5")}>
      <div
        className={cn(
          "overflow-hidden shadow-sm ring-1 ring-zinc-200/80",
          compactContext ? "rounded-xl" : "space-y-4",
        )}
      >
        <ProjectDetailHeader
          project={project}
          canDelete={canDelete}
          onDelete={() => void handleDelete()}
          backLabel={t("projects.backToList")}
          deleteLabel={t("common.delete")}
          sharedLabel={t("projects.sharedWithMe")}
          compact={compactContext}
        />
        <ProjectBalanceCards
          project={project}
          opening={opening}
          spent={spent}
          remaining={remaining}
          overBudget={overBudget}
          compact={compactContext}
        />
      </div>

      <div className="va-project-tabs-shell overflow-hidden rounded-xl border border-zinc-200/80 bg-white shadow-sm">
        <div className="border-b border-zinc-100 bg-gradient-to-r from-zinc-50/90 via-white to-teal-50/30 px-3 pt-2 sm:px-4">
          <Tabs tabs={tabs} active={activeTab} onChange={setTab} variant="pills" dense={compactContext} />
        </div>

        {project.is_shared && collaboratorRoleLabel ? (
          <p className="border-b border-teal-100 bg-teal-50/60 px-4 py-2 text-xs text-teal-900">
            {t("projects.collaboratorAccessHint", { role: collaboratorRoleLabel })}
          </p>
        ) : null}

        <div className={cn(compactContext ? "p-3 sm:p-4" : "p-4 sm:p-6")}>
          {loading ? (
            <PageLoader layout="embedded" message={t("common.loadingProject")} />
          ) : null}
          {!loading && !tabAllowed ? (
            <PageLoader layout="embedded" message={t("common.loading")} />
          ) : null}
          {!loading && tabAllowed && activeTab === "overview" ? (
            <OverviewTab project={project} onUpdate={setProject} />
          ) : null}
          {!loading && tabAllowed && activeTab === "ingestion" ? (
            <IngestionTab
              project={project}
              onCostsChanged={() => void refreshBalance()}
              onProjectUpdated={() => void loadProject({ silent: true })}
            />
          ) : null}
          {!loading && tabAllowed && activeTab === "analysis" ? (
            <AnalysisTab project={project} />
          ) : null}
          {!loading && tabAllowed && activeTab === "collaboration" ? (
            <CollaborationTab project={project} />
          ) : null}
          {!loading && tabAllowed && activeTab === "reports" ? (
            <ReportsTab project={project} />
          ) : null}
          {!loading && tabAllowed && activeTab === "financing" ? (
            <ProjectFinancingTab project={project} />
          ) : null}
        </div>
      </div>
    </div>
  );
}
