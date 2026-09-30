import { apiRequest, buildQuery } from "@/lib/api/http-client";
import type { ChatPollResponse, NotificationsResponse } from "@/lib/types/notifications";

const inflightListRequests = new Map<string, Promise<NotificationsResponse>>();

export const notificationsApi = {
  list(params?: { limit?: number; offset?: number; unread_only?: boolean }) {
    const query = buildQuery(params ?? {});
    const cacheKey = query || "default";
    const existing = inflightListRequests.get(cacheKey);
    if (existing) return existing;

    const request = apiRequest<NotificationsResponse>(`/notifications${query}`, "GET").finally(
      () => {
        inflightListRequests.delete(cacheKey);
      },
    );
    inflightListRequests.set(cacheKey, request);
    return request;
  },

  markRead(id: string) {
    return apiRequest<{ unread_count: number }>(`/notifications/${id}/read`, "PATCH");
  },

  markAllRead() {
    return apiRequest<{ unread_count: number }>("/notifications/read-all", "POST");
  },

  pollChat(projectId: string, afterId?: string) {
    return apiRequest<ChatPollResponse>(
      `/projects/${projectId}/chat/poll${buildQuery({ after_id: afterId })}`,
      "GET",
    );
  },

  markChatRead(projectId: string, messageId?: string) {
    return apiRequest<{ message: string }>(`/projects/${projectId}/chat/read`, "POST", {
      message_id: messageId,
    });
  },

  chatPresence(projectId: string) {
    return apiRequest<{ online: ChatPollResponse["online"] }>(
      `/projects/${projectId}/chat/presence`,
      "POST",
      {},
    );
  },
};
