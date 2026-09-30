import { apiRequest, buildQuery } from "@/lib/api/http-client";
import type { AdminUserSubscription } from "@/lib/types/admin";
import type { User } from "@/lib/types/auth";

interface PaginatedUsers {
  items: User[];
  total: number;
  limit: number;
  offset: number;
}

export const usersApi = {
  list(params?: { is_active?: boolean; role?: string; limit?: number; offset?: number }) {
    const query: Record<string, string | number | undefined> = {
      limit: params?.limit ?? 100,
      offset: params?.offset ?? 0,
    };
    if (params?.is_active !== undefined) {
      query.is_active = params.is_active ? "true" : "false";
    }
    if (params?.role) query.role = params.role;
    return apiRequest<PaginatedUsers>(`/admin/users${buildQuery(query)}`, "GET");
  },
  update(
    userId: string,
    payload: Partial<Pick<User, "full_name" | "is_active" | "role" | "bank_code">>,
  ) {
    return apiRequest<User>(`/admin/users/${userId}`, "PATCH", payload);
  },
  updateRole(userId: string, role: User["role"], bank_code?: string | null) {
    return apiRequest<User>(`/admin/users/${userId}/role`, "PATCH", { role, bank_code });
  },
  approve(
    userId: string,
    payload: {
      role?: "financial" | "user";
      plan_id?: string;
      access_days?: number;
    },
  ) {
    return apiRequest<{
      user: User;
      subscription: AdminUserSubscription | null;
      message: string;
    }>(`/admin/users/${userId}/approve`, "POST", payload);
  },
  extendAccess(userId: string, payload: { plan_id: string; access_days: number }) {
    return apiRequest<{ subscription: AdminUserSubscription; message: string }>(
      `/admin/users/${userId}/extend-access`,
      "POST",
      payload,
    );
  },
};
