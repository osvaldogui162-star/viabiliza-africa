import { apiRequest } from "@/lib/api/http-client";
import type { AdminOfficeSummary, OfficeDashboard, OfficeMember } from "@/lib/types/office";

function ownerQuery(ownerId?: string) {
  return ownerId ? `?owner_id=${encodeURIComponent(ownerId)}` : "";
}

export const officeApi = {
  dashboard(ownerId?: string) {
    return apiRequest<OfficeDashboard>(`/office/dashboard${ownerQuery(ownerId)}`, "GET");
  },

  members(ownerId?: string) {
    return apiRequest<{ items: OfficeMember[]; total: number }>(
      `/office/members${ownerQuery(ownerId)}`,
      "GET",
    );
  },

  createMember(
    payload: {
      email: string;
      full_name: string;
      job_title: string;
      notes?: string;
    },
    ownerId?: string,
  ) {
    const q = ownerQuery(ownerId);
    return apiRequest<OfficeMember>(`/office/members${q}`, "POST", payload);
  },

  updateMember(
    memberId: string,
    payload: { full_name?: string; job_title?: string; notes?: string | null },
  ) {
    return apiRequest<OfficeMember>(`/office/members/${memberId}`, "PATCH", payload);
  },

  archiveMember(memberId: string) {
    return apiRequest<OfficeMember>(`/office/members/${memberId}`, "DELETE");
  },

  assignProjects(
    memberId: string,
    payload: {
      assignments: {
        project_id: string;
        permission?: "view" | "collaborate";
        capabilities?: Record<string, boolean>;
      }[];
    },
  ) {
    return apiRequest<{ results: unknown[]; member_id: string }>(
      `/office/members/${memberId}/assign-projects`,
      "POST",
      payload,
    );
  },

  memberAccess(memberId: string) {
    return apiRequest<{
      member_id: string;
      items: {
        project_id: string;
        project_name: string;
        permission: string;
        effective_capabilities: Record<string, boolean>;
      }[];
      total: number;
    }>(`/office/members/${memberId}/access`, "GET");
  },

  adminListOffices() {
    return apiRequest<{ items: AdminOfficeSummary[]; total: number }>("/admin/offices", "GET");
  },
};
