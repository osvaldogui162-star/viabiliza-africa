import type { Project } from "@/lib/types/project";

export type ProjectTabId =
  | "overview"
  | "ingestion"
  | "analysis"
  | "collaboration"
  | "reports"
  | "financing";

export function projectTabAllowed(project: Project, tab: ProjectTabId, role?: string): boolean {
  if (role === "admin" || project.is_owner) return true;
  const caps = project.my_access?.effective_capabilities;
  if (!caps) return tab === "overview";

  switch (tab) {
    case "overview":
      return caps.view_project === true;
    case "ingestion":
      return caps.manage_ingestion === true || caps.manage_costs === true;
    case "analysis":
      return caps.run_analysis === true || caps.view_project === true;
    case "collaboration":
      return caps.manage_collaboration === true;
    case "reports":
      return caps.manage_reports === true;
    case "financing":
      return caps.view_financing === true;
    default:
      return false;
  }
}

export function collaboratorCanEditProject(project: Project, role?: string): boolean {
  if (role === "admin" || project.is_owner) return true;
  return project.my_access?.effective_capabilities?.edit_project === true;
}
